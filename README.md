# gitsum
`gitsum` is a command-line tool that provides a summary of multiple Git repositories.

## Installation
- Ensure you have Python 3.8+ installed.
- Clone this repository.
- Install the required dependencies using `pip install -r requirements.txt`.
- (For Linux users) Grant execution permission to the script using `chmod u+x gitsum.py`.
- Add this repository to your `PATH` environment variable.

## Usage
Move to a directory in which there are Git repositories.

On Windows, run
```bat
gitsum
```

On Linux, run
```sh
gitsum.py
```

This will print out an overview of the status of each repository within the current directory (or its subdirectories). For example:
```
   aaa               main
!  bbb               feature       * >1 <3
   ccc         [LR]  (no commits)
   subdir/ddd  [LB]  (f26dd4)
```

- `aaa`, `bbb`, `ccc`, and `sudir/ddd` are the names of the repositories (relative to the current working directory).
- `[LR]` indicates that the given repo has _no_ remotes (i.e., this is a local repo), while `[LB]` indicates that the repo has one or more remotes but the current `HEAD` has no upstream (e.g., it has not been pushed, it is detached).
- The `*` for repo `bbb` indicates that there are local changes (e.g., untracked files, modified files, deleted files).
- `>1` and `<3` say that `bbb` is 1 commit ahead and 3 commits behind its upstream branch, respectively.
