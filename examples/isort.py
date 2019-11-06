import textwrap

import copyist.helpers

ISORT_CONFIG = textwrap.dedent(
    """
    [tool.isort]
    # This section is managed by copyist - DO NOT EDIT DIRECTLY
    multi_line_output = 3
    use_parentheses = true
    include_trailing_comma = true
    force_grid_wrap = 0
    combine_as_imports = true
    line_length = 88
    lines_after_imports = 2
    force_single_line = true
    force_sort_within_sections = true
    known_first_party = ["{package_name}"]
    known_third_party = ["pytest"]
    """
).strip()


def apply_config(previous_content, context):
    return copyist.helpers.fill_tool_section(
        previous_content,
        "isort",
        section_text=ISORT_CONFIG.format(package_name=context["package_name"]),
    )
