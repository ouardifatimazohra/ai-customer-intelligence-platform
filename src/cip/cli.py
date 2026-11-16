"""Interface en ligne de commande `cip`.

Exemples :
    cip --version
    cip data download
    cip data verify
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from cip import __version__
from cip.data.dataset import TELCO_CHURN, DatasetIntegrityError, download_dataset, verify_file
from cip.log import configure_logging

DEFAULT_RAW_DIR = Path("data/raw")

app = typer.Typer(
    help="AI Customer Intelligence Platform — commandes d'exploitation.",
    no_args_is_help=False,
    add_completion=False,
)
data_app = typer.Typer(help="Acquisition et vérification des données sources.")
app.add_typer(data_app, name="data")


def _version(value: bool) -> None:
    if value:
        typer.echo(f"AI Customer Intelligence Platform v{__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version, is_eager=True, help="Affiche la version."),
    ] = False,
) -> None:
    configure_logging()
    if ctx.invoked_subcommand is None:
        typer.echo(f"AI Customer Intelligence Platform v{__version__}")
        typer.echo("Utilisez `cip --help` pour la liste des commandes.")


@data_app.command("download")
def data_download(
    dest: Annotated[Path, typer.Option(help="Dossier de destination.")] = DEFAULT_RAW_DIR,
    force: Annotated[bool, typer.Option(help="Retélécharger même si le fichier existe.")] = False,
) -> None:
    """Télécharge le dataset IBM Telco et vérifie son empreinte SHA-256."""
    try:
        path = download_dataset(dest, force=force)
    except DatasetIntegrityError as exc:
        typer.secho(f"ÉCHEC — {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from exc
    typer.secho(f"OK — {path} (SHA-256 {TELCO_CHURN.sha256[:12]}…)", fg=typer.colors.GREEN)


@data_app.command("verify")
def data_verify(
    dest: Annotated[Path, typer.Option(help="Dossier contenant le dataset.")] = DEFAULT_RAW_DIR,
) -> None:
    """Vérifie l'empreinte du dataset déjà téléchargé."""
    path = dest / TELCO_CHURN.filename
    if not path.exists():
        typer.secho(f"ABSENT — {path} (lancer `cip data download`)", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    try:
        digest = verify_file(path, TELCO_CHURN.sha256)
    except DatasetIntegrityError as exc:
        typer.secho(f"ÉCHEC — {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from exc
    typer.secho(f"OK — {path} conforme (SHA-256 {digest})", fg=typer.colors.GREEN)
