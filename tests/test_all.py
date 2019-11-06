import sys
import textwrap

import pytest
import tomlkit

from copyist import cli
from copyist import helpers
from copyist import sync


@pytest.fixture(scope="session", autouse=True)
def fake_sync_module():
    class fake_sync_module:
        @staticmethod
        def ensure_toto(previous_content, context):
            return "toto"

        @staticmethod
        def ensure_odd_number_of_o(previous_content, context):
            if not previous_content.count("o") % 2:
                return previous_content + "o"
            return previous_content

        @staticmethod
        def ensure_black_section(previous_content, context):
            return helpers.fill_tool_section(
                previous_content, "black", "[tool.black]\nline-length = 88\n",
            )

        @staticmethod
        def ensure_with_context(previous_content, context):
            prefix = context["prefix"]
            if not previous_content.startswith(prefix):
                return prefix + previous_content
            return previous_content

    sys.modules["fake_sync_module"] = fake_sync_module


def test_config(tmpdir):
    pyproject_file = tmpdir.join("pyproject.toml")
    pyproject_file.write(
        textwrap.dedent(
            """
        [tool.copyist]
        [tool.copyist.context]
        foo = "bar"
        [tool.copyist.files]
        test=["fake_sync_module.ensure_toto"]
        "pyproject.toml"=["fake_sync_module.ensure_black_section"]
        """
        ).strip()
    )
    generator, context = cli.read_configuration(str(pyproject_file))
    assert context == {"foo": "bar"}
    assert generator == {
        "test": ["fake_sync_module.ensure_toto"],
        "pyproject.toml": ["fake_sync_module.ensure_black_section"],
    }


def test_new_file(monkeypatch, tmpdir):
    monkeypatch.chdir(tmpdir)
    sync.sync_files(
        {"test": ["fake_sync_module.ensure_toto"]}, context={},
    )
    with open("test") as f:
        assert f.read() == "toto"


def test_overwrite_file(monkeypatch, tmpdir):
    monkeypatch.chdir(tmpdir)
    with open("test", "w") as f:
        f.write("tata")
    sync.sync_files(
        {"test": ["fake_sync_module.ensure_toto"]}, context={},
    )
    with open("test") as f:
        assert f.read() == "toto"


def test_update_file(monkeypatch, tmpdir):
    monkeypatch.chdir(tmpdir)
    with open("test", "w") as f:
        f.write("oo")
    sync.sync_files(
        {"test": ["fake_sync_module.ensure_odd_number_of_o"]}, context={},
    )
    with open("test") as f:
        assert f.read() == "ooo"


def test_combined(monkeypatch, tmpdir):
    monkeypatch.chdir(tmpdir)
    with open("test", "w") as f:
        f.write("xxx")
    sync.sync_files(
        {
            "test": [
                "fake_sync_module.ensure_toto",
                "fake_sync_module.ensure_odd_number_of_o",
            ]
        },
        context={},
    )
    with open("test") as f:
        assert f.read() == "totoo"


def test_ensure_toml(monkeypatch, tmpdir):
    pyproject_file = tmpdir.join("pyproject.toml")
    pyproject_file.write(
        textwrap.dedent(
            """
        [tool.copyist]
        [tool.copyist.files]
        "pyproject.toml" = ["fake_sync_module.ensure_black_section"]
        """
        ).strip()
    )

    monkeypatch.chdir(tmpdir)
    sync.sync_files(
        {"pyproject.toml": ["fake_sync_module.ensure_black_section"]}, context={},
    )
    with open("pyproject.toml") as f:
        data = tomlkit.parse(f.read())

    assert data["tool"]["black"]["line-length"] == 88
    # copyist configuration is still here
    assert data["tool"]["copyist"]


def test_with_context(monkeypatch, tmpdir):
    monkeypatch.chdir(tmpdir)
    sync.sync_files(
        {"test": ["fake_sync_module.ensure_with_context"]},
        context={"prefix": "foobar"},
    )
    with open("test") as f:
        assert f.read() == "foobar"