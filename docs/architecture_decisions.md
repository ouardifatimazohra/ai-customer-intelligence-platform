# Décisions d'architecture (ADR)

Format court : contexte → décision → conséquences. Une décision n'est jamais modifiée en place : elle est remplacée par une nouvelle ADR qui la référence.

| ADR | Décision | Statut | Date |
|---|---|---|---|
| 001 | Dataset IBM Telco figé par SHA-256 | Validée (étudiante) · licence à confirmer par l'encadrant | 16/11/2026 |
| 002 | Périmètre MVP / complémentaire / optionnel | Validée (étudiante) · à présenter à l'encadrant | 16/11/2026 |
| 003 | Pas d'Airflow au MVP : orchestrateur en ligne de commande | Validée | 16/11/2026 |
| 004 | SQL versionné plutôt que dbt (dbt conditionnel en S3) | Validée | 16/11/2026 |
| 005 | LLM : API Groq (offre gratuite) + mode `mock` sans clé | Validée | 16/11/2026 |
| 006 | Couche RAW en colonnes TEXT plutôt qu'en JSONB | Validée | 16/11/2026 |
| 007 | Python 3.12 et uv | Validée | 16/11/2026 |
| 008 | Seuil de décision par coût FN:FP = 5:1 (provisoire) | Validée, à revoir en S5 | 16/11/2026 |
| 009 | Développement en environnement cloud, vérification Windows par la CI | Validée | 16/11/2026 |
| 010 | Date de début et jours non travaillés | **En attente** de réponse | — |
| 011 | Contrainte 100 % gratuit | Validée | 16/11/2026 |
| 012 | Migrations SQL maison plutôt qu'Alembic | Prise en cours de réalisation | 16/11/2026 |
| 013 | Pandera + règles SQL plutôt que Great Expectations | Validée (cadrage) | 16/11/2026 |

---

## ADR-001 — Dataset figé par empreinte
- **Contexte** : le fichier distant peut changer ; les résultats (qualité, métriques) doivent être reproductibles.
- **Décision** : source officielle `IBM/telco-customer-churn-on-icp4d`, SHA-256 `16320c9c…3055e91`, vérifié à chaque téléchargement et avant profilage.
- **Conséquences** : tout fichier différent est rejeté (code 2). Licence Apache 2.0 du dépôt ; IBM ne publie pas de licence propre aux données → validation encadrant demandée.

## ADR-003 — Orchestration sans Airflow au MVP
- **Contexte** : pipeline de ~5 étapes, déclenché à la demande, sur 7 043 lignes. Airflow ajoute 3 à 4 services et environ 4 Go de RAM recommandés.
- **Décision** : commande `cip pipeline run` idempotente (carte DE-005).
- **Conséquences** : pas de planification ni d'interface de suivi au MVP ; Airflow documenté en perspective (DE-007, P2).

## ADR-005 — LLM Groq et mode mock
- **Contexte** : contrainte de gratuité ; la CI ne doit dépendre d'aucune clé.
- **Décision** : interface `LLMClient` avec deux implémentations, `groq` (clé `GROQ_API_KEY` dans `.env`) et `mock` (déterministe, par défaut). La configuration refuse `LLM_PROVIDER=groq` sans clé (implémenté, DO-003).
- **Conséquences** : les quotas de l'offre gratuite limitent le débit (gestion des erreurs 429 prévue en AI-001). Les embeddings seront calculés localement (gratuits, hors-ligne).

## ADR-006 — RAW en colonnes TEXT
- **Contexte** : le CDC proposait `payload_json`.
- **Décision** : une colonne `TEXT` par colonne source, plus `ingestion_id`, `source_row_number` et `loaded_at`.
- **Conséquences** : fidélité totale à la source (aucune conversion), requêtes de staging simples. Justifié par le profilage : les 11 valeurs `" "` de `TotalCharges` sont conservées telles quelles.

## ADR-009 — Environnement de développement et vérification Windows
- **Contexte** : l'étudiante travaille sous Windows sans uv installé ; le développement est fait dans un environnement cloud.
- **Décision** : la CI exécute les tests sous `ubuntu-latest` **et** `windows-latest` à chaque PR.
- **Conséquences** : la compatibilité Windows est prouvée automatiquement. La vérification sur le poste réel de l'étudiante reste prévue en DO-007 (sprint 8).

## ADR-011 — Contrainte 100 % gratuit
- **Décision** : outils open source uniquement ; Groq en offre gratuite ; GitHub Actions sur dépôt public ; Trello gratuit (pas de champs personnalisés : priorité et estimation écrites dans la description des cartes) ; aucune publication d'image Docker vers un registre payant.

## ADR-012 — Runner de migrations maison
- **Contexte** : une dizaine de tables prévues ; besoin de migrations traçables et rejouables.
- **Décision** : fichiers `database/migrations/NNNN_nom.sql`, table `app.schema_migration` avec empreinte SHA-256, une transaction par migration, verrou consultatif PostgreSQL. Une migration appliquée ne peut plus être modifiée.
- **Conséquences** : pas de migration descendante automatique (on crée une nouvelle migration). Code court et lisible, testé contre un vrai PostgreSQL.

## ADR-013 — Data Quality sans Great Expectations
- **Décision** : Pandera pour le schéma côté Python, règles SQL maison historisées dans `app.data_quality_result`.
- **Conséquences** : mêmes dimensions mesurées (complétude, unicité, validité, cohérence, fraîcheur) avec moins de dépendances.

Les ADR 002, 004, 007, 008 et 010 sont détaillées dans [`cadrage/00_cadrage_phase0.md`](cadrage/00_cadrage_phase0.md) §3, §4.3 et §6.
