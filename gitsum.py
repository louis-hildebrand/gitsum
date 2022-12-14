from pathlib import Path
import argparse
import os

import lib.search as search
import lib.status as status


def _show_git_summary(fetch: bool, list_outside_files: bool, only_outside_files: bool) -> None:
    cwd = Path(os.getcwd())
    repos = search.find_git_repos(cwd, list_outside_files or only_outside_files)
    if only_outside_files:
        return

    print(f"Found {len(repos)} Git repositories.")
    statuses = [status.get_repo_status(r, fetch) for r in repos]
    name_width = max([len(s.name) for s in statuses])
    head_width = max([len(s.head) for s in statuses])
    statuses.sort(key=lambda s: s.name)
    [print(s.to_string(name_width, head_width)) for s in statuses]


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="gitsum",
        description="View a summary of statuses for multiple Git repositories."
    )
    parser.add_argument("-f", "--fetch", action="store_true", help="fetch before getting status")
    parser.add_argument("-o", "--outside-files", action="store_true", help="list files and directories that are not inside a Git repository")
    parser.add_argument("-O", "--only-outside-files", action="store_true", help="list files and directories that are not inside a Git repository and exit")
    args = parser.parse_args()

    _show_git_summary(args.fetch, args.outside_files, args.only_outside_files)


main()
