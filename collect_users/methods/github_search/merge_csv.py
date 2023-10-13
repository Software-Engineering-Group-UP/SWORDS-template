"""
Script Overview:
This script is designed to traverse a root directory, identify CSV files with the same name,
and merge their contents. The merged CSV files are saved in the root directory.
"""

import os
from collections import defaultdict

import pandas as pd


def merge_csv_files(root_directory):
    """
    Traverses the root directory to find CSV files with the same name and merges their contents.

    Args:
        root_directory (str): The root directory to begin the search and merge operation.

    Returns:
        None: The merged CSV files are saved in the root directory.
    """
    # Dictionary to store file names and their paths
    csv_files_dict = defaultdict(list)

    print(f"Starting to scan from root directory: {root_directory}")

    # Traverse each folder to find CSV files
    for dir_path, _, file_names in os.walk(root_directory):
        print(f"Scanning directory: {dir_path}")

        for file_name in file_names:
            if file_name.endswith('.csv'):
                full_path = os.path.join(dir_path, file_name)
                print(f"Found CSV file: {full_path}")
                csv_files_dict[file_name].append(full_path)

    # Group the CSV files with the same name and merge them
    for file_name, file_paths in csv_files_dict.items():
        if len(file_paths) > 1:  # Check if there are multiple files with the same name
            print(f"Merging files for: {file_name}")
            try:
                data_frames = [pd.read_csv(file_path) for file_path in file_paths]
                merged_data_frame = pd.concat(data_frames, ignore_index=True)

                # Save the merged CSV files in the root directory
                merged_file_path = os.path.join(root_directory, f"merged_{file_name}")
                merged_data_frame.to_csv(merged_file_path, index=False)
                print(f"Merged {file_name} and saved as merged_{file_name} in the root directory.")
            except Exception as error:  # pylint: disable=broad-except
                print(f"Error while merging {file_name}: {error}")
        else:
            print(f"Only one file found for {file_name}. No merging required.")
