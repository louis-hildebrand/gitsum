# gitsum
`gitsum` is a command-line tool that provides a summary of multiple Git repositories.

## Installation
- Ensure you have Python 3.8+ installed.
- Clone this repository.
- Install the required dependencies using `pip install -r requirements.txt`.
- (For Linux users) Grant execution permission to the script using `chmod u+x gitsum`.
- Add this repository to your `PATH` environment variable.

## Usage
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

### Interpretation of Output
- `[LR]` indicates that the given repo has _no_ remotes (i.e., this is a local repo), while `[LB]` indicates that the repo has one or more remotes but the current `HEAD` has no upstream (e.g., it has not been pushed, it is detached).
- `*` indicates that there are local changes (e.g., untracked files, modified files, deleted files).
- `>1` and `<3` say that the given repo is 1 commit ahead and 3 commits behind its upstream branch, respectively.

## Running the Tests
The tests can be run by issuing the command `pytest` (or `python -m unittest`, if you prefer). This must be done from the root of the repository.

`gitsum` is verified by a few integration tests which create Git repos and check that the command's output is as expected. To avoid the `gitsum` repo itself interfering with the output, the repo is temporarily disabled by renaming the `.git/` folder. This might not be possible if your IDE is using the `.git/` folder. If you get errors, you might need to disable your IDE's Git integration for this project. For example, in VS Code, you can add a file `.vscode/settings.json` in the root of the repo with the following contents:
```json
{
    "git.enabled": false
}
```
