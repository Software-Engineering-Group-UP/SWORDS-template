"""
Script Overview:
This script fetches contributors of a specified GitHub repository and saves them to a CSV file.
It utilizes the GitHub API through the ghapi library.
"""

import argparse
from datetime import datetime
from pathlib import Path
import os
import pandas as pd
from ghapi.all import GhApi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def fetch_contributors(repository, owner, api_instance):
    """
    Fetch contributors of a specified GitHub repository.

    Args:
    - repository (str): Name of the GitHub repository.
    - owner (str): Owner of the GitHub repository.
    - api_instance (GhApi): Initialized GhApi instance for API operations.

    Returns:
    - List[dict]: List of contributors.
    """
    return api_instance.repos.list_contributors(owner, repository)


def save_to_csv(data_list, file_path):
    """
    Save the provided data to a CSV file.

    Args:
    - data_list (List[dict]): Data to be saved.
    - file_path (Path): Destination path for the CSV file.
    """
    data_frame = pd.DataFrame(data_list)
    data_frame.to_csv(file_path, index=False)


def main():
    """Main function to orchestrate the fetching and saving of contributor data."""
    # Initialize parser and parse command-line arguments
    parser = argparse.ArgumentParser(description='Fetch GitHub repository contributors.')
    parser.add_argument('--repo', required=True, help='GitHub repository name')
    parser.add_argument('--owner', required=True, help='GitHub repository owner')

    args = parser.parse_args()
    repo_name = args.repo
    repo_owner = args.owner

    # Initialize GitHub API
    api_instance = GhApi(token=os.getenv('GITHUB_TOKEN'))

    # Ensure the 'results' and organization directories exist
    results_directory = Path("results")
    results_directory.mkdir(parents=True, exist_ok=True)

    org_directory = results_directory / repo_owner
    org_directory.mkdir(parents=True, exist_ok=True)

    # Fetch contributors and prepare data
    contributors_list = fetch_contributors(repo_name, repo_owner, api_instance)
    current_date = datetime.today().strftime('%Y-%m-%d')
    data_list = [{'user_id': contributor.login, 'date': current_date, 'service': 'GitHub.com'}
                 for contributor in contributors_list]

    # Save data to CSV and notify user
    csv_file_path = org_directory / f"{repo_name}_contributors.csv"
    save_to_csv(data_list, csv_file_path)
    print(f"Contributor data saved to {csv_file_path}")


if __name__ == '__main__':
    main()
