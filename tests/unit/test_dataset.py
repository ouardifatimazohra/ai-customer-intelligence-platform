"""Tests de l'acquisition du dataset (DE-001).

Aucun accès réseau : la source est simulée par une URL file://.
Le test réseau réel est marqué `network` et exclu de la CI par défaut.
"""

import hashlib
from dataclasses import replace

import pytest
from typer.testing import CliRunner

from cip.cli import app
from cip.data.dataset import (
    TELCO_CHURN,
    DatasetIntegrityError,
    download_dataset,
    sha256_file,
    verify_file,
)

CONTENT = b"customerID,Churn\n0001-AAAA,No\n0002-BBBB,Yes\n"
DIGEST = hashlib.sha256(CONTENT).hexdigest()


@pytest.fixture
def local_spec(tmp_path):
    source = tmp_path / "source" / "telco.csv"
    source.parent.mkdir()
    source.write_bytes(CONTENT)
    return replace(TELCO_CHURN, url=source.as_uri(), sha256=DIGEST, filename="telco.csv")


def test_sha256_matches_hashlib(tmp_path):
    f = tmp_path / "f.csv"
    f.write_bytes(CONTENT)
    assert sha256_file(f) == DIGEST


def test_verify_accepts_correct_file(tmp_path):
    f = tmp_path / "f.csv"
    f.write_bytes(CONTENT)
    assert verify_file(f, DIGEST) == DIGEST


def test_verify_rejects_altered_file(tmp_path):
    f = tmp_path / "f.csv"
    f.write_bytes(CONTENT + b"0003-CCCC,No\n")  # une ligne ajoutée
    with pytest.raises(DatasetIntegrityError, match="Empreinte SHA-256 inattendue"):
        verify_file(f, DIGEST)


def test_download_writes_verified_file(tmp_path, local_spec):
    path = download_dataset(tmp_path / "raw", local_spec)
    assert path.read_bytes() == CONTENT


def test_download_reuses_existing_conform_file(tmp_path, local_spec):
    dest = tmp_path / "raw"
    first = download_dataset(dest, local_spec)
    mtime = first.stat().st_mtime_ns
    second = download_dataset(dest, local_spec)
    assert second.stat().st_mtime_ns == mtime  # pas de nouveau téléchargement


def test_download_rejects_wrong_digest_and_leaves_no_file(tmp_path, local_spec):
    dest = tmp_path / "raw"
    bad = replace(local_spec, sha256="0" * 64)
    with pytest.raises(DatasetIntegrityError):
        download_dataset(dest, bad)
    assert list(dest.iterdir()) == []  # ni fichier final ni fichier temporaire


def test_existing_altered_file_is_detected(tmp_path, local_spec):
    dest = tmp_path / "raw"
    dest.mkdir()
    (dest / "telco.csv").write_bytes(b"corrompu")
    with pytest.raises(DatasetIntegrityError):
        download_dataset(dest, local_spec)


def test_insecure_url_scheme_is_refused(tmp_path, local_spec):
    with pytest.raises(ValueError, match="Schéma"):
        download_dataset(tmp_path, replace(local_spec, url="http://example.com/x.csv"))


def test_cli_verify_reports_missing_file(tmp_path):
    result = CliRunner().invoke(app, ["data", "verify", "--dest", str(tmp_path)])
    assert result.exit_code == 1


def test_cli_verify_reports_altered_file(tmp_path):
    (tmp_path / TELCO_CHURN.filename).write_bytes(b"corrompu")
    result = CliRunner().invoke(app, ["data", "verify", "--dest", str(tmp_path)])
    assert result.exit_code == 2


@pytest.mark.network
def test_real_download_matches_frozen_digest(tmp_path):
    """Télécharge réellement le dataset officiel (désactivé en CI)."""
    path = download_dataset(tmp_path)
    assert sha256_file(path) == TELCO_CHURN.sha256
