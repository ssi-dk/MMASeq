# Addition of new modules and features
Addition/removal of modules

## Description
<!-- Please, briefly describe which modules or features you have added. If you have removed anything, please provide your reasoning behind this -->
<!-- Thank you for your contribution!! -->

## Label
Immediately after submitting your Pull request make sure to post `/minor` as a comment. This adds the `minor` label and enable checks to continue.
If check fails before you add the label, you can restart the check by adding and removing the `minor` label manually



## Checklist before your work can be merged
- [ ] If I have added any modules, I have added the corresponding configurations to the appropriate `config/species_configs/*.yaml` files. A bare minimum includes `all.yaml`, `test.yaml`, but the module can only be used if you add to the relevant species config file.
- [ ] If I have removed any modules, I have navigated through **all** `config/species_configs/*.yaml` files and removed all configurations of the corresponding module.
- [ ] If I have included a new species, I have created an appropriate configuration file in the `config/species_configs` folder (Consider using `default.yaml` as template) -> I promise to use underscore (_) as the species name separator and NOT whitespaces or dots (.) 
- [ ] I have selected a publically available sample from ENA and added its download path to the `data/reads/reads.url` file
- [ ] I have metadatized the sample in the `data/samplesheet.tsv`, `data/samplesheet_small.tsv`, and `data/samplesheet_test.tsv` files 
- [ ] I have installed the branch locally
- [ ] I have tested my modules by executing the database and conda deployment feature using the `mmadeploy --update ...` command 
- [ ] I have tested my modules by executing the normal pipeline on the included datasets by running the `mmadeploy ...` command (without `--test` and `--update`)