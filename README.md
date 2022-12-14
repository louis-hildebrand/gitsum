# gitsum
[![Test gitsum](https://github.com/louis-hildebrand/gitsum/actions/workflows/main.yml/badge.svg)](https://github.com/louis-hildebrand/gitsum/actions/workflows/main.yml)

`gitsum` is a command-line tool that provides a summary of multiple Git repositories.

## Installation
- Ensure you have Python 3.8+ installed.
- Clone this repository.
- Install the required dependencies using `pip install -r requirements.txt`.
- (For *nix users) Grant execution permission to the script using `chmod u+x gitsum`.
- Add this repository to your `PATH` environment variable.

## Basic Usage
Move to a directory in which there are Git repositories and then run `gitsum`.

This will print out an overview of the status of each repository within the current directory (or its subdirectories). For example:
```
Found 7 Git repositories.
!  deleted                        [LR]  master        *
!  modified                       [LR]  (d02092)      *
   remote/empty                   [LB]  (no commits)
!  remote/not empty/ahead behind        main            >1 <3
!  remote/not empty/staged              feature       *
!  unmerged                       [LR]  main          *
!  untracked                      [LR]  (no commits)  *
```

- `[LR]` indicates that the given repo has _no_ remotes (i.e., this is a local repo), while `[LB]` indicates that the repo has one or more remotes but the current `HEAD` has no upstream (e.g., it has not been pushed, it is detached).
- `*` indicates that there are local changes (e.g., untracked files, modified files, deleted files).
- `>1` and `<3` say that the given repo is 1 commit ahead and 3 commits behind its upstream branch, respectively.

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
Before running the tests, install the test dependencies using `pip install -r test-requirements.txt`. The tests can be run by issuing the command `pytest` (or `python -m unittest`, if you prefer). This must be done from the root of the repository.

Note that the tests are meant to be run in Python 3.8 (the output is sightly different on Python 3.9!). If you normally use a different version of Python and are seeing tests failing due to small differences in the help message, consider setting up a virtual environment with
```sh
python3.8 -m venv .venv
.venv/Scripts/activate  # or .venv/bin/activate, depending on your system
```
(where `python3.8` may need to be replaced with the path to your Python 3.8 installation.)

`gitsum` is verified by a few integration tests which create Git repos and check that the command's output is as expected. To avoid the `gitsum` repo itself interfering with the output, the repo is temporarily disabled by renaming the `.git/` folder. This might not be possible if your IDE is using the `.git/` folder. If you get errors, you might need to disable your IDE's Git integration for this project. For example, in VS Code, you can add a file `.vscode/settings.json` in the root of the repo with the following contents:
```json
{
    "git.enabled": false
}
```
