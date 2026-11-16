"""Point d'entrée en ligne de commande : `cip` ou `python -m cip`.

Les sous-commandes (db, data, pipeline, rag...) seront ajoutées par les cartes concernées.
"""

from cip import __version__


def main() -> None:
    print(f"AI Customer Intelligence Platform v{__version__}")


if __name__ == "__main__":
    main()
