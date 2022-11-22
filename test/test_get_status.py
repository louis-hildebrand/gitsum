from pygit2 import Oid, Repository, Signature
import os
import pygit2
import unittest
import uuid

from gitsum import RepoStatus
import gitsum


# ----------------------------------------------------------------------------------------------------------------------
# Test helpers
# ----------------------------------------------------------------------------------------------------------------------
def _create_empty_repo() -> Repository:
    repo_path = f"test/test-repos/{uuid.uuid4().hex}/"
    return pygit2.init_repository(repo_path)


def _full_path(repo: Repository, filename: str) -> str:
    repo_root = repo.path[:-5]
    return repo_root + filename


def _create_file_in_repo(repo: Repository, filename: str) -> None:
    with open(_full_path(repo, filename), "w"):
        pass


def _add_all_in_repo(repo: Repository) -> None:
    index = repo.index
    index.add_all()
    index.write()


def _commit_in_repo(repo: Repository, ref_name: str, parents: list[Oid]) -> Oid:
    sig = Signature("git-summary tester", "git-summary tester")
    repo.create_commit(ref_name, sig, sig, "Initial commit", repo.index.write_tree(), parents)


def _create_repo_with_files(filenames: list[str]) -> Repository:
    repo = _create_empty_repo()
    for f in filenames:
        _create_file_in_repo(repo, f)
    _add_all_in_repo(repo)
    _commit_in_repo(repo, "HEAD", [])
    return repo


def _delete_file_in_repo(repo: Repository, filename: str) -> None:
    os.remove(_full_path(repo, filename))


def _make_merge_conflict_in_repo(repo: Repository, filename: str) -> None:
    full_file_path = _full_path(repo, filename)
    # Create new branch
    current_commit = repo.revparse_single(repo.head.target.hex)
    repo.branches.local.create("feature", current_commit)
    # Modify file in main branch
    with open(full_file_path, "w") as f:
        f.write("Hello there!")
    _add_all_in_repo(repo)
    _commit_in_repo(repo, "HEAD", [repo.head.target])
    # Modify file in different branch
    repo.checkout(repo.lookup_reference("refs/heads/feature").name)
    with open(full_file_path, "w") as f:
        f.write("General Kenobi, you are a bold one!")
    _add_all_in_repo(repo)
    _commit_in_repo(repo, "HEAD", [repo.head.target])
    repo.checkout(repo.lookup_reference("refs/heads/main").name)
    # Merge
    repo.merge(repo.branches["feature"].target)


# ----------------------------------------------------------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------------------------------------------------------
MAIN_BRANCH_NAME = "main"


class GetStatusTests(unittest.TestCase):
    def test_empty_repo(self):
        repo = _create_empty_repo()
        status = gitsum.get_status(repo, "test-repo")
        self.assertEqual(RepoStatus("test-repo", "(no commits)", True, False, False, 0, 0), status)

    def test_repo_with_file(self):
        repo = _create_repo_with_files(["committed.txt"])
        status = gitsum.get_status(repo, "test-repo")
        self.assertEqual(RepoStatus("test-repo", MAIN_BRANCH_NAME, True, False, False, 0, 0), status)

    def test_untracked(self):
        repo = _create_empty_repo()
        _create_file_in_repo(repo, "untracked.txt")
        status = gitsum.get_status(repo, "test-repo")
        self.assertEqual(RepoStatus("test-repo", "(no commits)", True, True, False, 0, 0), status)

    def test_deleted(self):
        repo = _create_repo_with_files(["committed.txt"])
        _delete_file_in_repo(repo, "committed.txt")
        status = gitsum.get_status(repo, "test-repo")
        self.assertEqual(RepoStatus("test-repo", MAIN_BRANCH_NAME, True, True, False, 0, 0), status)

    def test_modified(self):
        repo = _create_repo_with_files(["committed.txt"])
        with open(_full_path(repo, "committed.txt"), "w") as f:
            f.write("Hello there!")
        status = gitsum.get_status(repo, "test-repo")
        self.assertEqual(RepoStatus("test-repo", MAIN_BRANCH_NAME, True, True, False, 0, 0), status)

    def test_unmerged(self):
        repo = _create_repo_with_files(["committed.txt"])
        _make_merge_conflict_in_repo(repo, "committed.txt")
        status = gitsum.get_status(repo, "test-repo")
        self.assertEqual(RepoStatus("test-repo", MAIN_BRANCH_NAME, True, True, False, 0, 0), status)

    def test_staged(self):
        repo = _create_empty_repo()
        _create_file_in_repo(repo, "untracked.txt")
        _add_all_in_repo(repo)
        status = gitsum.get_status(repo, "test-repo")
        self.assertEqual(RepoStatus("test-repo", "(no commits)", True, True, False, 0, 0), status)

    # TODO: Test remote (clone empty repo, a few commits ahead, a few commits behind, etc.)
