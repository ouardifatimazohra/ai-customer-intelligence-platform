# Preuves et illustrations pour le rapport PFA

Chaque fichier est une capture **réelle**, prise automatiquement (navigateur Chromium sans session, 1400×900, échelle 2) sur les pages publiques du dépôt. La date de capture et la source sont indiquées ci-dessous. Aucune image n'est retouchée.

## Sprint 1 — capturées le 16/11/2026

| Fichier | Légende | Ce que la figure démontre | Source |
|---|---|---|---|
| `tests/S1_ci_run_green_linux_windows.png` | Figure — Exécution CI réussie de la PR #2 | Le lint (Ruff) puis les tests passent sur **Linux et Windows** ; la compatibilité avec le poste de développement Windows est vérifiée automatiquement. | [run 43904273765](https://github.com/ouardifatimazohra/ai-customer-intelligence-platform/actions/runs/43904273765) |
| `tests/S1_ci_run_red_lint_failure.png` | Figure — Exécution CI bloquée par une erreur de lint volontaire | Un import inutilisé (`F401`) fait échouer le job Ruff et les tests ne sont pas lancés : du code non conforme ne peut pas être fusionné. PR de démonstration fermée sans fusion. | [run 43904124486](https://github.com/ouardifatimazohra/ai-customer-intelligence-platform/actions/runs/43904124486) |
| `tests/S1_ci_actions_history.png` | Figure — Historique des exécutions GitHub Actions | Traçabilité : chaque push et PR déclenche la CI. | onglet Actions |
| `git/S1_github_repo_tree_develop.png` | Figure — Arborescence du dépôt (branche develop) | Organisation du code par domaine et fichiers de gouvernance (README, CONTRIBUTING, CHANGELOG, LICENSE). | branche `develop` |
| `git/S1_git_commits_develop.png` | Figure — Historique des commits de develop | Messages Conventional Commits, fusion via Pull Requests, statut CI (3/3) par commit. | commits `develop` |
| `git/S1_pull_requests_closed.png` | Figure — Liste des Pull Requests | Workflow une carte = une branche = une PR. | onglet Pull requests |
| `git/S1_pr2_do002_merged.png` | Figure — Pull Request #2 (DO-002) | Description structurée (objectif, changements, validation) et lien vers la carte Trello. | [PR #2](https://github.com/ouardifatimazohra/ai-customer-intelligence-platform/pull/2) |
| `tests/S1_log_sample_DO-003.txt` | Extrait — Journal applicatif | Logs horodatés avec identifiant de lot et masquage automatique d'une clé API logguée par erreur. | exécution locale |
| `tests/S1_dataset_download_DE-001.txt` | Extrait — Acquisition du dataset | Téléchargement depuis la source IBM, vérification SHA-256, réutilisation idempotente et rejet d'un fichier altéré. | exécution locale |
| `tests/S1_postgres_migrations_DB-001.txt` | Extrait — Base PostgreSQL et migrations | Service Docker sain, migrations idempotentes, 4 schémas créés, table de traçabilité, message clair si la base est arrêtée. | exécution locale |
| `eda/profiling_churn_distribution.png` | Figure — Répartition de la cible Churn (n = 7 043) | Déséquilibre des classes : 26,5 % de départs ; l'accuracy seule serait trompeuse. | `uv run cip data profile` |
| `eda/profiling_numeric_distributions.png` | Figure — Distribution des variables numériques | Pics d'ancienneté aux extrêmes (0–1 et 72 mois), population à bas forfait, forte asymétrie des charges totales. | `uv run cip data profile` |
| `eda/profiling_summary.json` | Données — Résumé de profilage | Source de tous les chiffres du dictionnaire de données (aucune saisie manuelle). | `uv run cip data profile` |
| `diagrams/architecture_mvp.png` | Figure — Architecture MVP en couches | Séparation présentation / services / traitements / données ; l'interface ne parle qu'à l'API ; couches de données RAW → STAGING → ANALYTICS + APP. | `docs/diagrams/architecture_mvp.html` |

Note : les commits produits par l'assistant apparaissent « Unverified » sur GitHub (signature non rattachée au compte de l'étudiante) ; les commits de fusion créés par GitHub apparaissent « Verified ».
