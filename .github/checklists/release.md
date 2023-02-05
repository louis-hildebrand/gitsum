# Release instructions

## Release to TestPyPI
These steps are based on the guide ["Packaging Python Projects"](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives).
1. Check out the most recent commit on the release branch.
2. In `src/gitsum/__init__.py`, temporarily add the suffix `rc0` to the version number (e.g., version `1.0.0` would become `1.1.0rc0`). Do not commit this change.
3. Move to the root of the repo.
4. If you do not yet have a virtual environment, create one using `python -m venv .venv` (using Python 3.8+).
5. Activate the virtual environment using `.venv/Scripts/activate`.
6. Ensure you have the `build` package installed by running `pip install --upgrade build`.
7. Delete the `dist/` folder, if it already exists.
8. Build the project using `python -m build`. This should generate two new files: `dist/gitsum-VERSION.tar.gz` and `dist/gitsum-VERSION-py3-none-any.whl` (where `VERSION` is the version of the new release).
9. Ensure you have the `twine` package installed by running `pip install --upgrade twine`.
10. Upload to `TestPyPI` by running the command `twine upload --repository testpypi dist/*`.
	1. For the username, enter `__token__`.
	2. For the password, use the TestPyPI token (including the "pypi-" prefix).
11. Install the package from TestPyPI using `pip install --index-url https://test.pypi.org/simple/ --no-deps gitsum==VERSION`, where `VERSION` is the version you just uploaded.
12. Try running the command. If there are problems, fix them and repeat the release to TestPyPI before continuing. At the very least, the following points should be checked:
	1. The version number from `gitsum --version` should match the updated value.
	2. The main success scenario should work for a reasonable variety of repositories.
13. Drop the "rc" suffix in the version number.
14. Merge the release branch into main but do not delete the release branch yet.
15. Check out the `main` branch locally and pull.

## Release to GitHub
1. Delete the `dist/` folder.
2. Run `python -m build` again to generate the build files with the correct package name.
3. Go to the [Releases page](https://github.com/louis-hildebrand/gitsum/releases/new).
4. Tag the release `vVERSION` (e.g., `v1.0.0` for version 1.0.0).
5. Set the target to `main`.
6. Title the release `gitsum TAG` (e.g., `gitsum v1.0.0` for version 1.0.0).
7. Copy the relevant section of the changelog into the release description.
8. Attach the build files from the `dist` folder.
9. Ensure the checkbox "Set as a pre-release" is unchecked and that "Set as the latest release" is checked.
10. Publish the release.

## Release to PyPI
1. Upload to `PyPI` by running the command `twine upload dist/*`.
2. Install the newest version of the package and check that it is working as expected.

## After the release
1. Delete the release branch.
2. Close the milestone for the release that was just completed.
3. Open a new milestone for the next release and start assigning issues to it.
