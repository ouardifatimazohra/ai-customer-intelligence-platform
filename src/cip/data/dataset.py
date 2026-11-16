"""Téléchargement reproductible et vérifié du dataset IBM Telco Customer Churn.

Principe : la version du dataset est *figée* par son empreinte SHA-256. Un fichier
dont l'empreinte diffère (source modifiée, téléchargement tronqué, fichier altéré)
est rejeté : le pipeline ne travaille jamais sur des données inattendues.

Le téléchargement est atomique : il est écrit dans un fichier temporaire, vérifié,
puis renommé. Un échec ne laisse jamais de fichier partiel à l'emplacement final.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from cip.log import get_logger

log = get_logger(__name__)

_CHUNK = 64 * 1024


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    url: str
    sha256: str
    filename: str
    license: str
    source_page: str


TELCO_CHURN = DatasetSpec(
    name="IBM Telco Customer Churn",
    url=(
        "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/"
        "master/data/Telco-Customer-Churn.csv"
    ),
    sha256="16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91",
    filename="telco_customer_churn.csv",
    license="Apache-2.0 (licence du dépôt IBM/telco-customer-churn-on-icp4d)",
    source_page="https://github.com/IBM/telco-customer-churn-on-icp4d",
)


class DatasetIntegrityError(Exception):
    """L'empreinte du fichier ne correspond pas à la version figée."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_file(path: Path, expected_sha256: str) -> str:
    """Retourne l'empreinte si elle est conforme, lève DatasetIntegrityError sinon."""
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise DatasetIntegrityError(
            f"Empreinte SHA-256 inattendue pour {path.name} : "
            f"attendu {expected_sha256}, obtenu {actual}"
        )
    return actual


def download_dataset(
    dest_dir: Path,
    spec: DatasetSpec = TELCO_CHURN,
    *,
    force: bool = False,
    timeout: float = 60.0,
) -> Path:
    """Télécharge le dataset dans `dest_dir` et vérifie son empreinte.

    Si un fichier conforme existe déjà, il est réutilisé (aucun téléchargement),
    sauf si `force=True`.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / spec.filename

    if target.exists() and not force:
        verify_file(target, spec.sha256)
        log.info("Dataset déjà présent et conforme : %s", target)
        return target

    if not spec.url.startswith(("https://", "file://")):
        raise ValueError(f"Schéma d'URL non autorisé : {spec.url}")

    log.info("Téléchargement de %s depuis %s", spec.name, spec.url)
    fd, tmp_name = tempfile.mkstemp(prefix=".download-", dir=dest_dir)
    tmp = Path(tmp_name)
    try:
        # URL fixe et contrôlée ci-dessus (https/file uniquement)
        with os.fdopen(fd, "wb") as out, urllib.request.urlopen(spec.url, timeout=timeout) as resp:  # noqa: S310
            for chunk in iter(lambda: resp.read(_CHUNK), b""):
                out.write(chunk)
        verify_file(tmp, spec.sha256)
        tmp.replace(target)  # renommage atomique
    except Exception:
        tmp.unlink(missing_ok=True)
        raise

    log.info("Dataset téléchargé et vérifié (%d octets) : %s", target.stat().st_size, target)
    return target
