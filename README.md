# gitsum
[![Linux build badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/louis-hildebrand/cc9f4d1c6c0152b11b3eb2fe84fc0076/raw/gitsum-Linux.json)](https://github.com/louis-hildebrand/gitsum/actions/workflows/main-push.yml)
[![macOS build badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/louis-hildebrand/cc9f4d1c6c0152b11b3eb2fe84fc0076/raw/gitsum-macOS.json)](https://github.com/louis-hildebrand/gitsum/actions/workflows/main-push.yml)
[![Windows build badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/louis-hildebrand/cc9f4d1c6c0152b11b3eb2fe84fc0076/raw/gitsum-Windows.json)](https://github.com/louis-hildebrand/gitsum/actions/workflows/main-push.yml)
[![Coverage badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/louis-hildebrand/cc9f4d1c6c0152b11b3eb2fe84fc0076/raw/gitsum-coverage.json)](https://github.com/louis-hildebrand/gitsum/actions/workflows/main-push.yml)

`gitsum` is a command-line tool that provides a summary of multiple Git repositories.

## Installation
Ensure you have Python 3.8+ and pip installed. Then run
```sh
pip install gitsum
```

## Basic Usage
Move to a directory in which there are Git repositories and then run `gitsum`.

This will print out an overview of the status of each repository within the current directory (or its subdirectories). For example:
```
Found 7 Git repositories.
!  deleted                        master        *  local repo
!  modified                       (d02092)      *  local repo
   remote/empty                   (no commits)     local branch
!  remote/not empty/ahead behind  main             >1 <3
!  remote/not empty/staged        feature       *
!  unmerged                       main          *  local repo
!  untracked                      (no commits)  *  local repo
```

The standard output includes:
- The flag `!` if there are local changes or if the current branch is ahead of or behind its upstream branch
- The directory path (relative to the current working directory)
- The current branch (or the current commit hash if the repo is in detached HEAD mode)
- The flag `*` if there are local changes (e.g., untracked files, modified files, deleted files)
- The remote status, which can be:
    - `local repo` if the repository has no remotes
    - `local branch` if the repository has at least one remote but the current branch has no upstream
    - The number of commits ahead and behind the upstream branch (e.g., `>1 <3` say that the given repo is 1 commit ahead and 3 commits behind)

## General Usage
### Getting Help
Run
```sh
gitsum --help
```

### Listing Files Outside Git Repos
In some cases you might want to know if there are files or directories which are not in a Git repository (e.g., to know if you forgot to make a Git repo for any of your local projects).

To see a list of files and directories that are not inside a Git repository (in addition to the normal output), run
```sh
gitsum --outside-files
```

To see _only_ these outside files (without the normal output), run
```sh
gitsum --only-outside-files
```

### Fetching Beforehand
To fetch from each remote repository before displaying the repository statuses, run
```sh
gitsum --fetch
```

Note that this option is currently limited to public repositories. If `gitsum` is unable to fetch (e.g., because the repository is private), then a warning will simply be displayed. 

## Running the Tests
Before running the tests, clone the repository and install the test dependencies using `pip install -r test-requirements.txt`. You must also build the project with `python -m build` and then install the package with `pip install --find-links=dist gitsum`.

The tests can be run by issuing the command `pytest` (or `python -m unittest`, if you prefer). This must be done from the root of the repository.

`gitsum` is verified by a few integration tests which create Git repos and check that the command's output is as expected. To avoid the `gitsum` repo itself interfering with the output, the repo is temporarily disabled by renaming the `.git/` folder to `.git.bak/`. This might not be possible if your IDE is using the `.git/` folder. If you get errors, you might need to disable your IDE's Git integration for this project. For example, in VS Code, you can add a file `.vscode/settings.json` in the root of the repo with the following contents:
```json
{
    "git.enabled": false
}
```
