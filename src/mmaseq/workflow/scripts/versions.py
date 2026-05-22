import pandas as pd
from pathlib import Path
import yaml
from conda.core.prefix_data import PrefixData

deploy_dir = snakemake.input.deploy_dir
versions_file = snakemake.output.versions_file

conda_dir = Path(f"{deploy_dir}/conda").absolute()

versions_list = []
for conda_path in conda_dir.iterdir():

    if conda_path.suffix == ".yaml":
        with open(conda_path, "r") as yaml_read:
            try:
                conda_env = yaml.safe_load(yaml_read)
            except yaml.YAMLError as e:
                print(e)
    else:    
        continue
    try:
        records = PrefixData(conda_path.with_suffix('')).iter_records()
    except Exception as e:
        print("failed")
    
    for rec in records:
        if rec.name == conda_env.get("name"):
            version = rec.version.replace(rec.name, "")
            versions_list.append({"Tool": rec.name, "Version": version})

    versions = pd.DataFrame(versions_list)

    versions.to_csv(versions_file, sep = "\t", index = False)
