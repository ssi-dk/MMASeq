#!/usr/bin/env python3
import pandas as pd
from pathlib import Path
from collections import defaultdict

def module_statuses(samples, outdir):

    statuses = list()
    module_statuses = list()

    for sample_name, sample in samples.items():
        # Ensure consistency between sample class name and samples dictionary sample name
        if sample_name is not sample.name:
            raise ValueError("Sample class name inconsistency.\n - Sample class sample.name: {sample.name}\n - Sample dictionary sample_name: {sample_name}")

        # Iterate thorugh sample modules
        for module_name, module in sample.modules.items():
            if module.ignore:
                continue

            # Record status for all modules
            statuses.append(module.status())


            status = "Missing"
            if module.status:
                status = "Succeeded"

            module_statuses.append({
                "sample": sample_name,
                "module": {"name": module_name, "status": status}
            })

    module_status_file = outdir / "module_status.tsv"

    pd.DataFrame(module_statuses).to_csv(
        module_status_file,
        sep="\t",
        index=False
    )

    if not all(statuses):
        for status_info in module_statuses:
            name = status_info.get("sample")
            module = status_info.get("module")
            print(f"{name} - {module.get("name")}: {module.get("status")} ")
    else:
        print("All modules for all samples was executed successfully!")
        

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



def generate_long_results(samples):
    """
    Generates a concatenated long-format DataFrame from all result files.

    Args:
        all_result_files (defaultdict): Nested dictionary with sample -> module -> list of Path objects.

    Returns:
        pd.DataFrame: Concatenated long-format DataFrame from all result files.
    """
    all_sample_results = list()

    for sample_name, sample in samples.items():

        files = sample.all_results()
        for file in files:
            mod = file.parent.name

            try:
                sample_results = pd.read_csv(file, sep = "\t", index_col = False)
            except pd.errors.EmptyDataError:
                print(f"Results file {file.name} for {sample_name} is empty. Skipping!")
                continue

            # Determine whether the long table format is already observed
            sample_long = sample_results

            required_columns = {
                "Sample", "Module", "File", "Row", "Column", "Value"
            }
            if not required_columns.issubset(sample_results.columns):
                sample_long = unpivot_results(sample_name, mod, file, sample_results)

            all_sample_results.append(sample_long)

    return pd.concat(all_sample_results, ignore_index = True)
