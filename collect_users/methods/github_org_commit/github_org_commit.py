"""
Script Overview:
This script fetches members of a specified GitHub organization and saves them to a CSV file.
It utilizes the GitHub API and requires a GitHub token and user agent for authentication.
"""

import argparse
from datetime import datetime
import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USER")


def get_organization_members(org_name):
    """
    Fetch members of the specified GitHub organization.

    Args:
        org_name (str): Name of the GitHub organization.

    Returns:
        DataFrame: Contains user_id, date, and service columns.
                   Empty DataFrame if the organization has no members or if there's an error.
    """
    url = f"https://api.github.com/orgs/{org_name}/members"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "User-Agent": GITHUB_USER
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except (requests.RequestException, requests.Timeout) as error:
        print(f"HTTP Error: {error}")
        return pd.DataFrame()

    members_data = response.json()
    if not members_data:
        print("No members found for the organization.")
        return pd.DataFrame()

    user_ids = [member['login'] for member in members_data]
    current_date = datetime.now().strftime("%Y-%m-%d")

    data_frame = pd.DataFrame({
        'user_id': user_ids,
        'date': [current_date] * len(user_ids),
        'service': ['github'] * len(user_ids)
    })

    return data_frame


def save_members_to_csv(data_frame, org_name):
    """Save member data to a CSV file."""
    results_dir = 'results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    file_path = os.path.join(results_dir, f'{org_name}_members.csv')
    try:
        data_frame.to_csv(file_path, index=False, encoding='utf-8')
        print(f"Saved members of organization {org_name} "
              f"to {file_path}")
    except IOError as error:
        print(f"Failed to save CSV: {error}")


def main():
    """Main function for the script."""
    parser = argparse.ArgumentParser(description='Fetch members and save to CSV.')
    parser.add_argument('--org', required=True, help='GitHub organization name')
    args = parser.parse_args()

    members_data_frame = get_organization_members(args.org)
    if not members_data_frame.empty:
        save_members_to_csv(members_data_frame, args.org)
    else:
        print(f"Failed to fetch members of organization {args.org}")


if __name__ == "__main__":
    main()
