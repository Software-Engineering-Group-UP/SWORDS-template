"""
This file retrieves Github usernames from the Github API.
"""

import argparse
from datetime import datetime
from pathlib import Path
import os

import pandas as pd
from fastcore.foundation import L
from ghapi.all import GhApi, pages


class Service:  # pylint: disable=too-few-public-methods
    """
    Common variables used in functions bundled in Service class.
    """

    def __init__(self, api: GhApi):
        self.api = api
        self.api_service = "github.com"
        self.current_date = datetime.today().strftime('%Y-%m-%d')
        self.columns = ["service", "date", "user_id"]


def get_complete_query_result(query, query_type, service: Service):
    """Executes a search query and returns the result."""
    query_func = {
        "SEARCH_REPOS": service.api.search.repos,
        "SEARCH_USERS": service.api.search.users
    }.get(query_type)

    if not query_func:
        raise ValueError("Invalid query_type provided")

    query_func(query, per_page=100)
    last_page = service.api.last_page() or 1
    query_result = pages(query_func, last_page, query)

    result = L()
    for page in query_result:
        result.extend(page["items"])
    return result


def get_users_from_repos(repos, service: Service):
    """Retrieves the user from repositories data."""
    return L([service.api_service, service.current_date, repo["owner"]["login"]] for repo in repos)


def get_users_from_users(users, service: Service):
    """Retrieves the user from users data."""
    return L([service.api_service, service.current_date, user["login"]] for user in users)


def main():
    """Main function for the script."""
    serv = Service(GhApi(token=os.getenv('GITHUB_TOKEN')))

    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", "-t", help="set topic search string")
    parser.add_argument("--search", "-s", help="set general search string")
    args = parser.parse_args()

    try:
        if args.topic:
            print(f"Searching topics for {args.topic}...")
            topic_repos = get_complete_query_result(f"topic:{args.topic}", "SEARCH_REPOS", serv)
            ids_topic_repos = get_users_from_repos(topic_repos, serv)
            pd.DataFrame(ids_topic_repos, columns=serv.columns).to_csv(
                Path("results", "github_search_topic.csv"), index=False)
            print("Searching topics done")

        if args.search:
            print(f"Searching repos for {args.search}...")
            search_repos = get_complete_query_result(args.search, "SEARCH_REPOS", serv)
            ids_search_repos = get_users_from_repos(search_repos, serv)
            pd.DataFrame(ids_search_repos, columns=serv.columns).to_csv(
                Path("results", "github_search_repos.csv"), index=False)
            print("Searching repos done")

            print(f"Searching users for {args.search}...")
            search_users = get_complete_query_result(args.search, "SEARCH_USERS", serv)
            ids_search_users = get_users_from_users(search_users, serv)
            pd.DataFrame(ids_search_users, columns=serv.columns).to_csv(
                Path("results", "github_search_users.csv"), index=False)
            print("Searching users done")

    except Exception as error:  # pylint: disable=broad-except
        print(f"Error occurred: {error}")
        if "403" in str(error):
            print("A HTTP Error 403 indicates that rate limits are reached. "
                  "Please try again in a few minutes.")


if __name__ == '__main__':
    main()
