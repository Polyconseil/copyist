import tomlkit


def fill_tool_section(previous_content, tool_name, section_text):
    """TOML Helper ensuring that a [tool.<tool_name>] section contains <section_text>"""
    current_state = tomlkit.parse(previous_content)

    tool_table = tomlkit.parse(section_text)["tool"][tool_name]

    if "tool" not in current_state:
        tool_table = tomlkit.table()
        # This is not public API but prevents a useless "[tool]" line
        tool_table._is_super_table = True
        current_state.add("tool", tool_table)

    if tool_name not in current_state["tool"]:
        current_state["tool"].add(tool_name, tool_table)
    else:
        current_state["tool"][tool_name] = tool_table

    return tomlkit.dumps(current_state)
