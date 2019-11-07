import argparse
import os
import sys

import tomlkit

from . import exceptions
from . import sync


try:
    import importlib_metadata
except ImportError:
    # Use third party library on Python < 3.8
    import importlib.metadata as importlib_metadata


# Special error codes
# according to http://tldp.org/LDP/abs/html/exitcodes.html,
# those shouldn't have confusing meaning
CONFIGURATION_NOT_FOUND = 10
UNSYNCED_FILES = 11


def parse_args():
    parser = argparse.ArgumentParser("copyist")
    parser.add_argument(
        "--version", action="version", version=importlib_metadata.version("copyist")
    )

    parser.add_argument(
        "--config",
        "-c",
        default="pyproject.toml",
        help="Configuration file (defaults to %(default)s)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Show the diff produced at each stage",
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=False, help="Do not overwrite files"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        default=False,
        help="Error if a file needs to be changed - Implies --dry-run",
    )
    return parser.parse_args()


def read_configuration(filename):
    if not os.path.exists(filename):
        raise exceptions.ConfigurationException(
            f"Could not find configuration file {filename}"
        )

    with open(filename) as conf_file:
        conf = tomlkit.parse(conf_file.read())

    if not conf.get("tool") or not conf["tool"].get("copyist"):
        raise exceptions.ConfigurationException(
            f"Section [tool.copyist] missing from {filename}"
        )

    copyist_conf = conf["tool"]["copyist"]
    return copyist_conf.get("files", {}), copyist_conf.get("context", {})


def main():
    options = parse_args()
    try:
        file_generators, context = read_configuration(options.config)
    except exceptions.ConfigurationException as e:
        print(e.args[0])
        sys.exit(CONFIGURATION_NOT_FOUND)

    try:
        changed = sync.sync_files(
            file_generators,
            context,
            verbose=options.verbose,
            dry_run=options.dry_run or options.check,
        )
    except exceptions.SyncException as e:
        print(e.args[0])
        sys.exit(1)

    if changed and options.check:
        print(f"Unsynced files: {', '.join(changed)}")
        sys.exit(UNSYNCED_FILES)


if __name__ == "__main__":
    main()
