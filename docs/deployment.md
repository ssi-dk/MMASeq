# Deployment

## Installation Guide

The latest version of **MMASeq** can be installed using [Conda](#conda-installation) or [micromamba](#conda-installation), or directly [from source](#install-from-source). In the case of installation from source, conda or micromamba is still required to create the necessary environments for the pipeline execution. 

!!! info
        MMASeq currently supports **Linux** and similar UNIX-like environments. **macOS** is currently under testing and is not fully supported yet.

---

### <a name="conda-installation"></a> Conda or MicromambaInstallation

Create a clean, isolated environment:

```bash
conda create -n mmaseq -c conda-forge -c bioconda 
```

Activate the enviroment

```bash
conda activate mmaseq
```

```bash
PLACEHOLDER FOR CONDA INSTALLATION INSTRUCTION
```
In a similar manner one can use micromamba to create and manage the environment:

```bash
micromamba create -n mmaseq -c conda-forge -c bioconda
micromamba activate mmaseq
PLACEHOLDER FOR MICROMAMBA INSTALLATION INSTRUCTION
```

### <a name="Install from source"></a> Install from source  

This section is for user who wants to install **MMASeq** directly from source (e.g., for reproducibility or to debug a release) or to work on a development branch. In this case, the user needs to clone the repository and install the package using pip. Before installing the package, it is recommended to create a clean conda or micromamba environment to avoid any dependency conflicts. The following commands can be used to set up the environment and install the package (using conda,but the same can be done with micromamba):

```bash
conda create -n mmaseq -c conda-forge -c bioconda 
conda activate mmaseq 
conda install conda-forge::pip bioconda::snakemake conda-forge::conda conda-forge::pandas
git clone https://github.com/ssi-dk/MMASeq.git
cd MMASeq
pip install . 
```

If the user wants to work on a development branch:

```bash
conda create -n mmaseq -c conda-forge -c bioconda "snakemake>=9.12.0"
pip install pandas
git clone https://github.com/ssi-dk/MMASeq.git
cd MMASeq
git switch dev    # work on the develop branch
git checkout -b new-feature-branch  # Create a new branch from dev to work on new changes
pip install .
``` 

!!! info
    In some systems the conda executable command might not be available  after installation for the environment or conflicting with other conda installations on different environments. In this case, the user can first try to check the executable path using the following command `which conda`.
    If the command returns a path to the conda executable pointing to the correct environment location e.g `/home/user/miniconda3/envs/mmaseq/bin/conda`, then the conda command should work as expected and consequently the pipeline. However, if the command returns a path pointing to a different location (e.g., `/home/user/miniconda3/bin/conda`), it indicates that the conda command is not correctly linked to the environment's bin directory. In this case, the user can try to add the correct path to the conda executable to their system's PATH variable or use the full path to the conda executable prior to run the pipeline. 


## Running the workflow

The pipeline is designed presents 3 utilities:
- `mmacreate`: Create input samplesheets for MMAseq
- `mmadeploy`: executable for deploying the necessary conda environments and databases in a specified directory. This script can be used independently to set up the required resources before running the pipeline. Moreover, it is used to run the test set, which is a predefined set of analyses using example data to verify that the pipeline is correctly installed and configured on the system.
- `mmaseq`: Execute the MMASeq pipeline using the specified input configurations and parameters. This is the main launcher of the pipeline and is responsible for parsing the input configurations, setting up the necessary environments and databases, and executing the Snakemake workflow according to the specified parameters.

### MMAcreate launcher

Create a samplesheet by scanning the input directory for sample files. The sample names will be inferred from the detected files, and used to populate a samplesheet. After samplesheet creation, the pipeline will be executed in dry-run mode (simulated run) to verify that the generated samplesheet is correctly formatted and that all the necessary files are correctly linked.

```bash
USAGE
    mmacreate [-h] --indir INDIR 
                   --outdir OUTDIR 
                   --verbosity {0,1,2}
                   --logfile LOGFILE

OPTIONS
    -h, --help           show this help message and exit
    --indir INDIR        Input directory MUST be specified if the samplesheet does not yet exist. Input directory will be screened for `.fasta` and `fastq.gz` files, sample_names will be inferred from the detected files, and used
                        to populate a samplesheet. After samplesheet creation, the pipeline will be executed in dry-run mode (simulated run)
    --outdir OUTDIR      Directory used for storing the samplesheet. Samplesheet will be stored in outdir as 'samplesheet.tsv'
    --verbosity {0,1,2}  Adjust the verbosity (Default: 0); 0: Minimal messages, 1: Debug messages, 2: Trace messages (development only)
    --logfile LOGFILE    If provided, will redirect log messages from STDOUT to logfile. (Default: None) Will be ignored if logfile parent folder doesn't exist.
```

### MMAdeploy launcher

Install environments and creates databases by executing MMAseq on an inbuilt test dataset. This is a good way to verify that the pipeline is correctly installed and configured on your system. It will execute a predefined set of analyses using example data, and it will help you familiarize with the expected input and output formats. When run the executable will setup of the [conda](#conda) environments and the different [databases](#databases) automatically in the specified deployment directory. By default, it is set to be in the current working directory, but it can be specified by the user when running the executable. If the specified deployment directory does not exist, it will be created. If it already exists and correctly specified in the launcher command, the executable will check for the presence of the required databases and environments before execution, and it will use them to run the test dataset. 

```bash
USAGE
    mmadeploy [-h] --deploy_dir DEPLOY_DIR
                   --update
                   --retries RETRIES
                   --threads THREADS
                   --verbosity {0,1,2}
                   --logfile LOGFILE]
                   
                   
OPTIONS
    -h, --help            show this help message and exit
    --deploy_dir DEPLOY_DIR Directory used to deploy virtual environment and databases used during pipeline execution. To reinstall environments and/or databases, remove the `conda/` and/or the `Databases/` folders in the deployment directory. (Default: /dpssi/home/scrsim/.local/share/mamba/envs/mambaseq/lib/python3.13/site-packages/mmaseq/Deploy)
    --update    Will force rerunning all rules, thus issuing database updates( Default: False). The small dataset consists of a single isolate, executed on ALL modules, thus all results should be considered wrong. Read data will be downloaded to /dpssi/home/scrsim/.local/share/mamba/envs/mambaseq/lib/python3.13/site-packages/mmaseq/data/reads
    --retries RETRIES     Amount of attempts allowed for each file, when downloading the dataset (Default: 3). Setting this to 0 will lead to failure if any short instance of disconnect occurs. Contrarily, setting this to a too high value could lead to long run time if any continuous connection issue occurs. It's recommended to allow for a handful of attempts.
    --threads THREADS     Amount of threads (cores) to dedicate for executing the pipeline. (Default: 4)
    --verbosity {0,1,2}   Adjust the verbosity (Default: 0); 0: Minimal messages, 1: Debug messages, 2: Trace messages (development only)
    --logfile LOGFILE     If provided, will redirect log messages from STDOUT to logfile. (Default: None) Will be ignored if logfile parent folder doesn't exist.
```

### MMASeq launcher

The pipeline is designed to be run using the executable mmaseq.py, which is the main launcher of the pipeline. The launcher is responsible for parsing the input configurations, setting up the necessary environments and databases, and executing the Snakemake workflow according to the specified parameters. When run for the first time the pipeline will setup the conda environments and databasesunless previously deployed with `mmadeploy`, in that case the pipeline will use the existing onez in the specified folder.

```bash

USAGE
mmaseq [-h] --samplesheet SAMPLESHEET_FILE 
            --deploy_dir DEPLOY_DIR 
            --outdir OUTDIR 
            --config CONFIG 
            --threads THREADS 
            --resolve 
            --clean 
            --force 
            --ignore_assemblies 
            --verbosity {0,1,2} 
            --logfile LOGFILE
OPTIONS
    -h, --help            show this help message and exit
    --samplesheet SAMPLESHEET_FILE  Path to samplesheet TSV used by the pipeline. If the samplesheet doesn't exist, `indir` must be specified to create one.
    --deploy_dir DEPLOY_DIR Directory used to deploy virtual environment and databases used during pipeline execution. To reinstall environments and/or databases, remove the `conda/` and/or the `Databases/` folders in the
                        deployment directory. (Default: /dpssi/home/scrsim/.local/share/mamba/envs/mambaseq/lib/python3.13/site-packages/mmaseq/Deploy)
    --outdir OUTDIR       Directory used for storing analysis results.
    --config CONFIG       Configuration file location. (Default: /dpssi/home/scrsim/.local/share/mamba/envs/mambaseq/lib/python3.13/site-packages/mmaseq/config/config.yaml)
    --threads THREADS     Amount of threads (cores) to dedicate for executing the pipeline. (Default: 4)
    --resolve             Resolves absolute paths from samplesheet columns, will overwrite samplesheet. (Default: False)
    --clean               Remove intermediate folders and files after completion. (Default: True) If disabled, intermediate folders are maintained as OUTDIR/SAMPLE/raw/MODULE/ while result files are copied to
                        OUTDIR/SAMPLE/MODULE/
    --force               Force running all rules. (Default: False) This will cause all necessary rules for a given run to be executed, which e.g. run assemblies despite preexisting ones existing. Mostly useful for forcing deployment, or rerunning a suspicious batch.
    --ignore_assemblies   Avoid creating symbolic links of the assemblies into the pipeline output directory. (Default: False) If this is not specified, symbolic links will be created to the output directory, hence avoiding assembly steps in the pipeline. Use this option to enforce the pipeline to create assemblies (Will take extra time) rather than relying on those specified in the samplesheet.
    --verbosity {0,1,2}   Adjust the verbosity (Default: 0); 0: Minimal messages, 1: Debug messages, 2: Trace messages (development only)
    --logfile LOGFILE     If provided, will redirect log messages from STDOUT to logfile. (Default: None) Will be ignored if logfile parent folder doesn't exist.
```


### Run the test set

Running the test set is a good way to verify that the pipeline is correctly installed and configured on your system. It will execute a predefined set of analyses using example data, and it will help you familiarize with the expected input and output formats. To run the test set, simply execute the following command:

```bash
mmadeploy --deploy_dir path/to/deploy_dir --update --threads 4
```


### Run the pipeline on your data
Run the pipeline with the following command:

```bash
mmaseq --samplesheet path/to/samplesheet.tsv 
       --deploy_dir path/to/deploy_dir 
       --outdir path/to/output_dir
```


## Final report

All the workflow results are stored in the output directory specified by `--outdir`. 
The final output is a file named "all_results.tsv". This file is a concatenated file of all the collected output that can be further processed by the user.
It is in the following format:

| sample_name | tool | filename | organism | row_index | row | value |
| --- | --- | --- | --- | --- | --- | --- |
| Sample1 | resfinder | ResFinder_results_tab.txt | xxx | 1 | Resistance gene | xxx |
| Sample1 | plasmidfinder | results_tab.tsv |  | 1 | Accession number | xxx |
| Sample1 | virulencefinder | results_tab.tsv |  | 1 | Database | xxx |
....

## Configure workflow

This section is dedicated on how to configure and set up the different workflow components such as the input manager, the samplesheet and the species-specific configuration files. 

### Input manager configuration

We refer the main configuration file as "input manager" and contains all the informations regarding input, metadata, output etc...
It is formatted as the following:


```yaml
deploy_dir: folder/where/the/deployed/conda/envs/and/databases/are
outdir: /folder/where/to/store/the/results
samplesheet: path/to/samplesheet.tsv
```

Generally, this file is created automatically during pipeline execution, based on the input parameters provided by the user. However, it can also be created manually before running the pipeline, in which case it will be used as-is. If the file already exists and is correctly specified in the launcher command, the pipeline will not overwrite it.  

This behavior allows the user to maintain full control over configuration settings and tailor them to their specific needs. If the file does not exist, it will be generated during execution using the parameters supplied by the user, ensuring that all required configurations are available for the pipeline to run smoothly.

### Samplesheet configuration

The pipeline employs a samplesheet in the .tsv format to run all the analysis  in batch for the samples.
The format is the following:


| sample_name   |      Illumina_mate1     |    Illumina_mate2       |        Assembly        |          config             |
|---------------|-------------------------|-------------------------|------------------------|-----------------------------|
| Sample1       | path/to/read2.fastq.gz  | path/to/read2.fastq.gz  | path/to/assembly.fasta | path/to/species_config.yaml |
| Sample2       | path/to/read2.fastq.gz  | path/to/read2.fastq.gz  | path/to/assembly.fasta | path/to/species_config.yaml |
---

We included a "samplesheet.tsv" in the "data/" folder. This can be modified by the user to suit its need. 


### Species-specific configuration

Certain species may require different tools than those currently defined or tool-specific parameters that differ from those used in other species. The options which distinguish them are defined in the species-specific configuration files.
The format is typical of a .yaml file, and is the following:

```yaml
mlst:
    assemblers: shovill  
    
resfinder:
    options: --species 'Other'

plasmidfinder:
    options: ""

virulencefinder:
    options: ""

serotypefinder:
    options: ""
          
amrfinder:
    assemblers: shovill
    options: ""
    
meningotype:
    assemblers: shovill

kmeraligner:
    database: elmDB
    options : -ID 80 -1t1 -cge
```


The analysis supported and their option are listed in the [supported analysis](supported_analysis.md) section of the documentation. Each species-specific configuration file can be linked to a sample in the samplesheet, allowing for flexible and tailored analysis across different organisms. This modular approach ensures that the pipeline can be easily adapted to a wide range of bacterial species and genomic contexts, making it a versatile tool for microbial genomics research and surveillance:


