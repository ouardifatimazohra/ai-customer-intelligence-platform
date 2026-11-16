"""Interface en ligne de commande `cip`.

Exemples :
    cip --version
    cip data download
    cip data verify
    cip db migrate
    cip db status
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from sqlalchemy.exc import OperationalError

from cip import __version__
from cip.data.dataset import TELCO_CHURN, DatasetIntegrityError, download_dataset, verify_file
from cip.db.engine import get_engine
from cip.db.migrate import MIGRATIONS_DIR, MigrationError, migrate, status
from cip.log import configure_logging

DEFAULT_RAW_DIR = Path("data/raw")

app = typer.Typer(
    help="AI Customer Intelligence Platform — commandes d'exploitation.",
    no_args_is_help=False,
    add_completion=False,
)
data_app = typer.Typer(help="Acquisition et vérification des données sources.")
app.add_typer(data_app, name="data")
db_app = typer.Typer(help="Base de données : migrations du schéma.")
app.add_typer(db_app, name="db")


def _db_unreachable(exc: OperationalError) -> typer.Exit:
    """Message lisible quand PostgreSQL n'est pas joignable (au lieu d'un traceback)."""
    reason = str(exc.orig).strip().splitlines()[0] if exc.orig else str(exc)
    typer.secho(
        f"ÉCHEC — PostgreSQL injoignable : {reason}\n"
        "Vérifier que le service tourne (`docker compose up -d postgres`) "
        "et les variables POSTGRES_* du fichier .env.",
        fg=typer.colors.RED,
        err=True,
    )
    return typer.Exit(code=3)


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


@db_app.command("migrate")
def db_migrate(
    directory: Annotated[Path, typer.Option(help="Dossier des migrations.")] = MIGRATIONS_DIR,
) -> None:
    """Applique les migrations SQL en attente (idempotent)."""
    try:
        applied = migrate(get_engine(), directory)
    except OperationalError as exc:
        raise _db_unreachable(exc) from exc
    except MigrationError as exc:
        typer.secho(f"ÉCHEC — {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from exc
    if applied:
        typer.secho(f"OK — {len(applied)} migration(s) appliquée(s) : {', '.join(applied)}")
    else:
        typer.secho("OK — base déjà à jour", fg=typer.colors.GREEN)


@db_app.command("status")
def db_status(
    directory: Annotated[Path, typer.Option(help="Dossier des migrations.")] = MIGRATIONS_DIR,
) -> None:
    """Affiche l'état de chaque migration."""
    try:
        rows = status(get_engine(), directory)
    except OperationalError as exc:
        raise _db_unreachable(exc) from exc
    for filename, state in rows:
        typer.echo(f"{state:<12} {filename}")
