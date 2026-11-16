# Changelog

Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) ; versions [SemVer](https://semver.org/lang/fr/).

## [Non publié]

### Ajouté
- Initialisation du dépôt : arborescence, `.gitignore`, `.env.example`, `pyproject.toml` (uv, Python 3.12), README, conventions de contribution, modèle de Pull Request (DO-001).
- Qualité de code : Ruff (lint + format), Pytest + couverture, hooks pre-commit (clés privées, gros fichiers, fichiers `.env`), CI GitHub Actions sur Linux et Windows (DO-002).
- Configuration centralisée (`cip.config`, pydantic-settings, secrets en `SecretStr`, validation au démarrage) et journalisation structurée (`cip.log` : identifiant de lot par contexte, masquage des secrets) (DO-003).
- Commande `cip` (Typer) ; `cip data download` / `cip data verify` : téléchargement atomique du dataset IBM Telco, version figée par SHA-256, rejet des fichiers altérés ; fiche de provenance `data/README.md` (DE-001).
- PostgreSQL 16.16 via Docker Compose (healthcheck, volume) ; migrations SQL versionnées (`cip db migrate` / `cip db status`) avec empreinte, transaction par migration, verrou consultatif ; schémas `raw`, `staging`, `analytics`, `app` ; job CI d'intégration PostgreSQL (DB-001).
- `cip data profile` : profilage calculé du dataset brut (résumé JSON, règles de cohérence, 2 figures) et dictionnaire de données `docs/data_dictionary.md` (RS-001).
- Documentation du sprint 1 : charte, exigences tracées, architecture (diagramme en couches), décisions ADR 001–013, difficultés techniques, journal hebdomadaire, squelettes des documents à venir, cadrage historique (DOC-S1).
