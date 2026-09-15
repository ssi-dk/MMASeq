# Development guide
You are very welcome to contribute to the repository.
The repository structure and pipeline foundation can be a bit confusing though, this page aims at explaining how you can fork the repository to your own github account, then how to install mmaseq in general and how to deploy your own changes, first locally and later to push them to the official repository.

## Local development
* First time: Install MMAseq locally through its conda package (e.g. `micromamba create -n mmaseq bioconda::mmaseq --yes`)
* For the repository on GitHub using the "Fork" button on the MMAseq repository site
* Download and clone your fork `git clone https://github.com/[YOURgithubUSER]/MMASeq.git ~/repos/mmaseq`
* Navigate into the repo folder `cd ~/repos/mmaseq`
* Activate the propper enviornment (e.g. `micromamba activate mmaseq`)
* Create and switch to a new branch henceforth reffered as [BRANCH] ( e.g. `git switch -c patch_shovill_fix`)
* Make your changes in whatever branch you wish (dev default), and install them locally `pip install ~/repos/mmaseq`
* Once satisfied, push your changes to your own fork `git push origin [BRANCH]`
* On your own fork, navigate to Pull requests tab and click New Pull Request, select **base repository**: *ssi-dk/MMAseq* **base**: *dev* and **head repository**: *[YOURgithubUSER]/MMAseq* **compare**: *[BRANCH]* 

## Type of Change
Add a label to this PR by commenting one of the following:
- `/build` - Minor documentation or general repository. These changes will not increment the software version upon successful merge
- `/patch` - Bugfixes and typos
- `/minor` - New features and software enhancements
- `/major` - Backwards incompatible changes (collaborators only)

**Note:** The label check waits 20 seconds before reading labels. Comment your label immediately after creating the PR to ensure the check passes.

## Checklist
Before creating a Pull request for your changes, you can save time by completing the following steps in advance, on you local repository.

### Special case

### Setup (Required for all PRs)
- [ ] I have installed the local branch (e.g. using `pip install .` in an appropriate virtual environment)

### For Adding or Removing Modules
- [ ] I have added my new module to / removed the old module from - the appropriate `.smk` file:
  - `PR_analysis.smk` for paired-end reads
  - `SR_analysis.smk` for single-end reads
  - `analysis.smk` for assembly-based analysis
- [ ] I have checked that the rule Output follows correct file naming conventions
- [ ] I have created/updated the appropriate species config in `mmaseq/src/mmaseq/config/species_configs/`
- [ ] I have added/removed the module alongside its configuration to both `test.yaml` and `all.yaml`
- [ ] I have included a sample and added its ftp link to `mmaseq/src/mmaseq/data/reads/reads.urls`
- [ ] I have updated the samplesheet at `mmaseq/src/mmaseq/data/samplesheet.tsv` (if needed)
- [ ] I have run a minimal test using `mmadeploy --test` and confirmed that my module completed succesfully
- [ ] I have added the `minor` label to my PR

### For other pipeline Changes
- [ ] I have that all my changes work using `mmadeploy --update`
- [ ] I have added the `patch` OR `minor` label (depending on the type of changes) to my PR

## Related Issues
<!-- Link any related issues: Closes #123 -->

