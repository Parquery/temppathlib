#!/usr/bin/env python3
"""Run precommit checks on the repository."""
import argparse
import os
import pathlib
import re
import subprocess
import sys


def main() -> int:
    """Execute the main routine."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--overwrite",
        help="Overwrites the unformatted source files with the "
        "well-formatted code in place. If not set, "
        "an exception is raised if any of the files do not conform "
        "to the style guide.",
        action='store_true')

    args = parser.parse_args()

    overwrite = bool(args.overwrite)

    repo_root = pathlib.Path(__file__).parent

    # yapf: disable
    source_files = (
                sorted((repo_root / "temppathlib").glob("**/*.py")) +
                sorted((repo_root / "tests").glob("**/*.py")))
    # yapf: enable

    if overwrite:
        print('Removing trailing whitespace...')
        for pth in source_files:
            pth.write_text(re.sub(r'[ \t]+$', '', pth.read_text(), flags=re.MULTILINE))

    print("YAPF'ing...")
    yapf_targets = ["tests", "temppathlib", "setup.py", "precommit.py"]
    if overwrite:
        # yapf: disable
        subprocess.check_call(
            ["yapf", "--in-place", "--style=style.yapf", "--recursive"] +
            yapf_targets,
            cwd=str(repo_root))
        # yapf: enable
    else:
        # yapf: disable
        subprocess.check_call(
            ["yapf", "--diff", "--style=style.yapf", "--recursive"] +
            yapf_targets,
            cwd=str(repo_root))
        # yapf: enable

    print("Mypy'ing...")
    subprocess.check_call(["mypy", "--strict", "temppathlib", "tests"], cwd=str(repo_root))

    print("Isort'ing...")
    # yapf: disable
    isort_files = map(str, source_files)
    # yapf: enable

    # yapf: disable
    subprocess.check_call(
        ["isort", "--project", "temppathlib", '--line-width', '120'] +
        ([] if overwrite else ['--check-only']) +
        [str(pth) for pth in source_files])
    # yapf: enable

    print("Pydocstyle'ing...")
    subprocess.check_call(["pydocstyle", "temppathlib"], cwd=str(repo_root))

    print("Pylint'ing...")
    subprocess.check_call(["pylint", "--rcfile=pylint.rc", "tests", "temppathlib"], cwd=str(repo_root))

    print("Testing...")
    env = os.environ.copy()
    env['ICONTRACT_SLOW'] = 'true'

    # yapf: disable
    subprocess.check_call(
        ["coverage", "run",
         "--source", "temppathlib",
         "-m", "unittest", "discover", "tests"],
        cwd=str(repo_root),
        env=env)
    # yapf: enable

    subprocess.check_call(["coverage", "report"])

    print("Doctesting...")
    doctest_files = ([repo_root / "README.rst"] + sorted((repo_root / "temppathlib").glob("**/*.py")))

    for pth in doctest_files:
        subprocess.check_call([sys.executable, "-m", "doctest", str(pth)])

    print("Checking setup.py sdist ...")
    subprocess.check_call([sys.executable, "setup.py", "sdist"], cwd=str(repo_root))

    print("Checking with twine...")
    subprocess.check_call(["twine", "check", "dist/*"], cwd=str(repo_root))

    return 0


if __name__ == "__main__":
    sys.exit(main())
