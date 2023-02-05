# Instructions for Making a Release

1. Create a new branch whose name starts with `release/` (e.g., `release/1.0.0` for version 1.0.0).
2. Increment the version number (see https://semver.org/).
3. Update the changelog
	1. Label all the issues in this release `published`. While doing so, double-check that all the user-facing ones have been added to the changelog.
	2. Replace the `[Unreleased]` section with the new version number and the date of the release.
	3. Add a new, empty section `[Unreleased]`.
4. Open a pull request from that branch to the main branch.

Further instructions should be provided automatically as a comment on the pull request.
