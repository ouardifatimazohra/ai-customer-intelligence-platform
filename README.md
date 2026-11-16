# AI-Powered Customer Intelligence Platform

Plateforme de bout en bout de **Data Engineering**, **Machine Learning** et **Generative AI** pour analyser les clients et prédire le churn (résiliation), avec un cas d'usage télécom basé sur le dataset public *IBM Telco Customer Churn*.

[![CI](https://github.com/ouardifatimazohra/ai-customer-intelligence-platform/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/ouardifatimazohra/ai-customer-intelligence-platform/actions/workflows/ci.yml)

> Projet de fin d'année (PFA), cycle ingénieur informatique — 8 semaines.
> **État actuel : sprint 1, initialisation du dépôt.** Les fonctionnalités ci-dessous sont **prévues** ; elles seront marquées comme livrées au fur et à mesure, avec preuves dans `docs/weekly_progress.md`.

## Fonctionnalités cibles (MVP)

| Domaine | Fonctionnalité | Statut |
|---|---|---|
| Data Engineering | Ingestion CSV traçable → PostgreSQL (RAW / STAGING / ANALYTICS) | prévu (S2–S3) |
| Data Quality | Règles mesurables historisées, rapport par lot | prévu (S3) |
| Machine Learning | Comparaison LogReg / Random Forest / XGBoost, seuil selon le coût métier | prévu (S4–S5) |
| Explainable AI | SHAP global et local | prévu (S5) |
| Generative AI | RAG avec citations + Text-to-SQL sécurisé (lecture seule) | prévu (S6) |
| Application | API FastAPI + interface Streamlit | prévu (S2–S7) |
| DevOps | Docker Compose, tests Pytest, CI GitHub Actions | prévu (S1–S8) |

## Stack (100 % gratuite / open source)

Python 3.12 · uv · PostgreSQL 16 · Pandas · Pandera · scikit-learn · XGBoost · SHAP · MLflow · sentence-transformers · FAISS · API Groq (offre gratuite, optionnelle grâce au mode `mock`) · FastAPI · Streamlit · Docker Compose · Pytest · Ruff · GitHub Actions.

## Démarrage rapide (développement)

Prérequis : Git et [uv](https://docs.astral.sh/uv/). Installation de uv sous Windows (PowerShell) :

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

uv installe lui-même Python 3.12 si nécessaire.

```powershell
git clone https://github.com/ouardifatimazohra/ai-customer-intelligence-platform.git
cd ai-customer-intelligence-platform
Copy-Item .env.example .env
uv sync
uv run pre-commit install   # contrôles automatiques avant chaque commit
uv run cip
```

Contrôles de qualité (les mêmes que la CI) :

```powershell
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

## Structure du dépôt

```
src/cip/            Code applicatif (package Python)
frontend/           Interface Streamlit
database/migrations Scripts SQL versionnés
transformations/sql Transformations STAGING / ANALYTICS
quality/reports     Rapports qualité générés (non versionnés)
data/               Données locales (non versionnées)
notebooks/          Analyses exploratoires
tests/              unit / integration / e2e
docs/               Documentation technique et du PFA
report_assets/      Figures et preuves pour le rapport
```

## Conventions

Branches, commits et Definition of Done : voir [CONTRIBUTING.md](CONTRIBUTING.md).

## Données

Le dataset n'est **pas** versionné : il est téléchargé depuis sa source officielle et vérifié par empreinte SHA-256 (voir `data/README.md`, carte DE-001).

## Licence

Code sous licence MIT (voir [LICENSE](LICENSE)). Le dataset IBM Telco Customer Churn reste soumis aux conditions de sa source.
