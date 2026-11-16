"""Tests « smoke » : le paquet s'importe et la commande `cip` s'exécute.

Ils vérifient l'installation elle-même (uv sync), sur Linux comme sur Windows en CI.
"""

import re
import subprocess
import sys

from typer.testing import CliRunner

import cip
from cip.cli import app


def test_package_exposes_semver_like_version() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+(\.dev\d+)?", cip.__version__)


def test_cli_version_option() -> None:
    result = CliRunner().invoke(app, ["--version"])
    assert result.exit_code == 0
    assert cip.__version__ in result.output


def test_module_is_executable_with_python_m() -> None:
    result = subprocess.run(  # noqa: S603 - commande fixe, aucune entrée externe
        [sys.executable, "-m", "cip"], capture_output=True, text=True, check=True
    )
    assert "AI Customer Intelligence Platform" in result.stdout
