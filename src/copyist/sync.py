import difflib
import importlib
import os.path

from . import exceptions


def _import_name(generator):
    """Import a class from its module name."""
    # A generator 'path'
    try:
        mod_name, func_name = generator.rsplit(".", 1)
    except ValueError:
        raise ValueError("Invalid generator class name %s" % generator)

    try:
        mod = importlib.import_module(mod_name)
    except ImportError as e:
        raise ValueError("Error importing generator module %s: '%s'" % (mod_name, e))

    try:
        return getattr(mod, func_name)
    except AttributeError:
        raise ValueError(
            "Module '%s' does not define a '%s' class" % (mod_name, func_name)
        )


def sync_files(file_generators, context, *, verbose=False, dry_run=False):
    changed = set()
    for filename, generators in file_generators.items():
        if os.path.exists(filename):
            with open(filename) as f:
                file_content = f.read()
        else:
            file_content = ""

        original_content = file_content

        for generator_name in generators:
            try:
                generator = _import_name(generator_name)
            except ValueError as e:
                raise exceptions.SyncException(
                    f"Could not find generator {generator_name} for {filename}: {e.args[0]}"
                )
            new_file_content = generator(file_content, context=context)
            if new_file_content != file_content:
                print(f"{filename}: updated by {generator_name}")
                if verbose:
                    diff = "\n".join(
                        difflib.unified_diff(
                            file_content.splitlines(),
                            new_file_content.splitlines(),
                            fromfile="before",
                            tofile="after",
                            lineterm="",
                        )
                    )
                    print(diff)
                file_content = new_file_content
            else:
                print(f"{filename}: up-to-date for {generator_name}")

        if original_content != file_content:
            changed.add(filename)
            if dry_run:
                print(f"{filename}: skipping write")
                continue

            with open(filename, "w") as f:
                f.write(new_file_content)
    return changed
