"""Point d'entrée en ligne de commande : `cip` ou `python -m cip`."""

from cip.cli import app


def main() -> None:
    app()


if __name__ == "__main__":
    main()
