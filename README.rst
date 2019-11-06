==============================================
copyist - Easily sync your configuration files
==============================================

To make sure all your projects share the same configuration, add a ``[tool.copyist]`` section to
the ``pyproject.toml`` file of your projects specifying the expected files and their generators.

For example, ``copyist``'s ``isort`` configuration is synced from ``examples/isort.py`` policy as specified
in its ``pyproject.toml``::

    [tool.copyist]
      [tool.copyist.context]
      package_name = "copyist"

      [tool.copyist.files]
      "pyproject.toml" = ["examples.isort.apply_config"]


Configuration
=============

``[tool.copyist.files]`` section lists the files to generate/keep synced with their list of generators to apply.

Each generator is a function taking as argument the previous content of the file and an optional context
specified in ``[tool.copyist.context]`` section.

The generators are generally provided by an other Python package specifying your expected configuration.


Command line options
====================

You can list them by running ``copyist --help``::

    usage: copyist [-h] [--version] [--config CONFIG] [--verbose] [--dry-run]

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      --config CONFIG, -c CONFIG
                            Configuration file (defaults to pyproject.toml)
      --verbose, -v         Show the diff produced at each stage
      --dry-run             Do not overwrite files


Helpers
=======

Currently only ``copyist.helpers.fill_tool_section(previous_content, tool_name, section_text)`` is available
to help fill ``pyproject.toml`` with the different tools' configurations.
