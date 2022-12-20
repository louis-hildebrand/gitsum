"""
Program entry point for testing purposes. Simply invokes gitsum.cli.main(). This is necessary because setuptools builds the project with its own entry point in src/ (so all imports need to be relative to src/), but I'd prefer to keep all modules (including cli) inside the gitsum package.
"""
import gitsum.cli

gitsum.cli.main()
