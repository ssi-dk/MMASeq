import argparse
from pathlib import Path
import base64
import requests
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument(
    "--output", "-o",
    type = str,
    dest = "output",
    default = "rMLST.tsv",
    help = "Output tsv file path."
)
parser.add_argument(
    "--assemblers", "-a",
    type = str,
    dest = "assemblers",
    default = None,
    help = "List of assemblers, is used to strip assemblers from sample_files for name extraction."
  )
parser.add_argument(
  '--file_list', '-f',
  type = str,
  nargs = '+',
  help = 'assembly contig filename (FASTA format)')

args = parser.parse_args()

def main(assembly_file, assemblers):
  all_good = True
  sample = str(assembly_file.stem)

  # Remove assemblers naming from the sample name (should only be one per run)
  if assemblers:
    for assembler in assemblers:
      sample = sample.lstrip(f"{assembler}_")
  print(sample, flush = True)
  
  uri = 'https://rest.pubmlst.org/db/pubmlst_rmlst_seqdef_kiosk/schemes/1/sequence'
  fasta_seqs = assembly_file.read_text()
  print(" - Encoding and uploading fasta", flush = True)
  payload = '{"base64":true,"details":true,"sequence":"' + base64.b64encode(fasta_seqs.encode()).decode() + '"}'
  retries = 0
  while retries < 5:
    retries += 1
    try:
      response = requests.post(uri, data=payload)
      print(" - Delineating response", flush = True)
      if response.status_code == requests.codes.ok:
        retries = 5
        data = response.json()
        try: 
          data['taxon_prediction']
        except KeyError:
          print(" - No rMLST match!", flush = True)
          data = {'taxon_prediction': {'taxon': "None", 'rank': "NA", 'support': 0}}
      else:
          print(f"Response status code not parrallel:\n - Response_status: {response.status_code}\n - Request_code: {requests.codes.ok} \nAttempt {retries} of 5 failed. Retrying!", flush = True)
    except ConnectionError:
      if retries < 5:
        warning(f"Attempt {retries} of 5 failed. Retrying!", flush = True)
      else:
        data = {'taxon_prediction': {'taxon': "rMLST Failed", 'rank': "FAILED", 'support': 0}}
        all_good = False



    match = pd.DataFrame(columns = ["Sample", "Match", "Species", "Rank", "Percentage"])

    for results in data['taxon_prediction']:
      try:
        taxon = results['taxon']
      except TypeError:
        print(f"Something most likely went wrong during deleniating response. Rerun rMLST on {sample}. Ignoring sample!", flush = True)
        all_good = False
        continue
      genus = taxon[0]
      family = taxon.split()[-1]
      species = "%s. %s" %(genus, family)

      match.loc[len(match.index)] = [sample, taxon, species, results['rank'], results['support']]
      print(f"  - Species: {species}\n")

    return(match)

  else:
    print(response.text, flush = True)

  if not all_good:
    print("Warning: One or multiple issues arrose during typing. Pay close attention to the log!", flush = True)    


if __name__ == "__main__":
  assemblies = [Path(assembly) for assembly in args.file_list]  
  assembly_list = args.file_list

  matches = list()
  rmlst = pd.DataFrame()

  for assembly_file in assemblies:
    match = main(assembly_file, args.assemblers)

    if match is not None:
      matches.append(match)

  rmlst = pd.concat(matches)

  output_path = args.output
  rmlst_file = Path(args.output)

  if not rmlst_file.parent.is_dir():
    rmlst_file.parrent.mkdir(parents = True)
  rmlst.to_csv(rmlst_file, sep = "\t", index = False)
  print("Success!", flush = True)
