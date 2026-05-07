#!/usr/bin/env python3

import pandas as pd
from pathlib import Path
from collections import defaultdict

# Import from utils
from .utils import deconvolute_path, read_results_catalogue


def define_module_results_file(outdir, sample, module, results_catalogue, sample_configs):
    """
    Defines the expected result file paths for a specific module and sample.

    Args:
        outdir (str): Output directory path.
        sample (str): Sample name.
        module (str): Module name.
        results_catalogue (dict): Dictionary containing result file templates for each module.
        sample_configs (dict): Dictionary containing configurations for each sample.

    Returns:
        list: List of Path objects representing the expected result file paths.
    """
    # Define prefix for result file paths
    prefix = Path(f"{outdir}/{sample}/{module}").expanduser()

    module_result_files = list()

    # Define and normalise expected reult file names
    result_strings = results_catalogue.get(module)
    if not isinstance(result_strings, (list, tuple)):
        result_strings = [result_strings]

    # Define module configurations
    sample_cfg = sample_configs.get(sample)
    configs = sample_cfg.get(module)

    # Define container for results
    module_result_files = []

    # Iterate over multiple expected output results files
    for template in result_strings:
        deconvoluted_paths = deconvolute_path(template, configs)

        for path in deconvoluted_paths:
            module_result_files.append(prefix / path)

    return module_result_files


def define_all_result_files(outdir, sample_configs, results_catalogue):
    """
    Defines all expected result file paths for all samples and modules.

    Args:
        outdir (str): Output directory path.
        sample_configs (dict): Dictionary containing configurations for each sample.
        results_catalogue (dict): Dictionary containing result file templates for each module.

    Returns:
        defaultdict: Nested dictionary with sample -> module -> list of Path objects.
    """
    # Define carrier object
    all_result_files = defaultdict(dict)

    # Iterate over individual sample configurations
    for sample, modules in sample_configs.items():
        
        # Iterate over individual modules
        for mod in modules.keys():

            # Ensure that module exists in results catalogue
            if mod not in results_catalogue.keys():
                continue
            
            # Define Result file strings
            result_strings = results_catalogue.get(mod)

            # Streamline object as list
            if type(result_strings) is not list:
                result_strings = [result_strings]

            # Extract the configurations as keywords
            configs = modules.get(mod)

            # Streamline object as dict
            if type(configs) is not dict:
                configs = dict() # Not a dict means no keywords

            result_files = define_module_results_file(outdir, sample, mod, results_catalogue, sample_configs)

            all_result_files[sample].update({mod: result_files})

    return all_result_files


def unpivot_results(sample, module, file, results):
    """
    Converts a wide-format results DataFrame to a long-format DataFrame.

    Args:
        sample (str): Sample name.
        module (str): Module name.
        file (Path): Path to the results file.
        results (pd.DataFrame): Wide-format results DataFrame.

    Returns:
        pd.DataFrame: Long-format DataFrame with columns Sample, Module, File, Row, Column, Value.
    """
    # Convert index to row number column starting from row 1
    results.index += 1
    results = results.reset_index(names = "Row")

    # Generate long list format of results file
    results_long = results.melt(
        id_vars = "Row",
        var_name = "Column",
        value_name = "Value"
        )

    # add columns in a single assignment (faster than multiple insert calls)
    results_long[["Sample", "Module", "File"]] = [sample, module, file.name]
    
    # if you want a specific column order:
    cols = ["Sample", "Module", "File", "Row", "Column", "Value"]
    results_long = results_long[cols]

    return results_long


def generate_long_results(all_result_files):
    """
    Generates a concatenated long-format DataFrame from all result files.

    Args:
        all_result_files (defaultdict): Nested dictionary with sample -> module -> list of Path objects.

    Returns:
        pd.DataFrame: Concatenated long-format DataFrame from all result files.
    """
    all_sample_results = list()

    for sample, modules in all_result_files.items():

        for mod, files in modules.items():

            long_mod_results = list()

            for file in files:

                try:
                    sample_results = pd.read_csv(file, sep = "\t", index_col = False)
                except pd.errors.EmptyDataError as e:
                    print(f"Results file {file.name} for {sample} is empty. Skipping!")
                    continue

                # Determine whether the long table format is allready observed
                sample_long = sample_results
                if not {"Sample", "Module", "File", "Row", "Column", "Value"}.issubset(sample_results.columns):
                    sample_long = unpivot_results(sample, mod, file, sample_results)

                all_sample_results.append(sample_long)

    return pd.concat(all_sample_results, ignore_index = True)


def determine_rule_output(outdir, sample, module, results_catalogue, sample_configs):
    """
    Determines the output paths for a rule based on the results catalogue and configurations.

    Args:
        outdir (str): Output directory path.
        sample (str): Sample name.
        module (str): Module name.
        results_catalogue (dict): Dictionary containing result file templates for each module.
        sample_configs (dict): Dictionary containing configurations for each sample.

    Returns:
        list: List of output path strings for the rule.
    """
    result_strings = results_catalogue.get(module)
    if not isinstance(result_strings, (list, tuple)):
        result_strings = [result_strings]

    # Define module configurations
    sample_cfg = sample_configs.get(sample)
    configs = sample_cfg.get(module)

    # Define container for results
    module_result_path = []

    # Iterate over multiple expected output results files
    for template in result_strings:
        deconvoluted_paths = deconvolute_path(template, configs)

        for path in deconvoluted_paths:
            module_result_path.append(path)

    return ["%s/{sample}/{module}/" %outdir + path for path in module_result_path]