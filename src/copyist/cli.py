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
        sys.exit(1)

    try:
        sync.sync_files(
            file_generators, context, verbose=options.verbose, dry_run=options.dry_run,
        )
    except exceptions.SyncException as e:
        print(e.args[0])
        sys.exit(1)


if __name__ == "__main__":
    main()
