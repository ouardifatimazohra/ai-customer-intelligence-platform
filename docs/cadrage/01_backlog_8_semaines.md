> **Document historique** — version présentée le 16/11/2026 *avant* validation. Les décisions validées et leur statut à jour sont dans [`../architecture_decisions.md`](../architecture_decisions.md) ; l'avancement réel dans [`../weekly_progress.md`](../weekly_progress.md).

# Backlog complet — 8 sprints hebdomadaires

> Statut : **proposition, rien n'est encore créé dans Trello.** Après validation, chaque carte sera créée dans le tableau
> « AI Customer Intelligence Platform — PFA », dans la liste *Product Backlog*. Les cartes du sprint courant passent dans *Sprint Backlog*.
>
> **Priorités** : P0 = MVP (chemin critique) · P1 = complémentaire · P2 = optionnel / abandonnable.
> **Estimation** en jours idéaux (j). Capacité par sprint : 5 j, dont ~1 j réservé (doc + imprévus).
> **Champs remplis à l'exécution** (vides tant que rien n'est fait) : *Branche*, *Commit(s)*, *PR*, *Statut réel*, *Preuves conservées*.
>
> **Labels Trello** : `Data Engineering` · `Database` · `ML` · `GenAI` · `Backend` · `Frontend` · `DevOps` · `Documentation` · `Bug` · `Research`.

Format de chaque carte : **ID — Titre** · label · priorité · estimation · dépendances
→ *Objectif* · *Tâches* · *Critères d'acceptation (CA)* · *Tests* · *Livrables / preuves*

---

## Sprint 1 — Cadrage, socle et étude du dataset · Jalon M1
**Livrable fonctionnel** : `docker compose up` démarre PostgreSQL avec les 4 schémas ; le dépôt est sur GitHub avec CI verte ; dataset figé et profilé.

**PM-001 — Validation du cadrage** · Research · P0 · 0,5 j · —
→ Faire valider le cadrage (périmètre, D1–D10) par l'étudiante puis l'encadrant.
Tâches : présenter `00_cadrage_phase0.md` ; consigner les décisions dans `docs/architecture_decisions.md`.
CA : chaque décision D1–D10 a un statut (validée / modifiée / reportée) et une date.
Preuves : compte rendu de réunion encadrant (date, décisions).

**PM-002 — Création du tableau Trello** · Documentation · P0 · 0,25 j · PM-001
→ Créer le tableau, les 8 listes, les 10 labels et les cartes de ce backlog.
CA : toutes les cartes présentes avec ID, labels, checklists ; capture du tableau.
Preuves : `report_assets/trello/S1_board_initial.png`.

**DO-001 — Initialisation du dépôt GitHub** · DevOps · P0 · 0,5 j · PM-001
→ Dépôt professionnel prêt à recevoir du code.
Tâches : arborescence (adaptée du §13 du CDC, package `src/cip/`), `.gitignore`, `.env.example`, `README.md`, `LICENSE`, `pyproject.toml` (uv, Python 3.12), branches `main`/`develop`, protection de `main`, modèle de PR, `CHANGELOG.md`.
CA : `uv sync` fonctionne sous Linux et Windows ; aucun secret ni donnée versionnés (`git ls-files` vérifié).
Tests : `uv run python -c "import cip"` ; `git check-ignore .env data/raw/x.csv`.
Preuves : capture de l'arborescence GitHub, `git log --oneline`.

**DO-002 — Qualité de code et CI minimale** · DevOps · P0 · 0,5 j · DO-001
→ Chaque push est vérifié automatiquement dès le premier jour.
Tâches : Ruff (lint + format), Pytest, pre-commit (ruff + détection de secrets), `.github/workflows/ci.yml`, 1 test « smoke ».
CA : CI verte sur `develop` ; une erreur de lint volontaire fait échouer la CI.
Preuves : capture de l'onglet Actions (run vert + run rouge volontaire).

**DO-003 — Configuration centralisée et logging** · Backend · P0 · 0,5 j · DO-001
→ Un seul point de configuration (pydantic-settings, `.env`) et des logs structurés horodatés.
CA : aucune valeur sensible en dur ; changement de `DATABASE_URL` sans modifier le code ; logs avec `ingestion_id` quand disponible.
Tests : unitaires sur le chargement de la config (valeurs par défaut, variable manquante → erreur claire).

**DB-001 — PostgreSQL dans Docker Compose + migrations** · Database · P0 · 1 j · DO-001
→ Base reproductible avec schémas `raw`, `staging`, `analytics`, `app`.
Tâches : `docker-compose.yml` (postgres 16, volume, healthcheck), `database/migrations/0001_schemas.sql`, runner de migrations idempotent (`cip db migrate`), table `app.schema_migration`.
CA : migration rejouable sans erreur ; `\dn` liste les 4 schémas.
Tests : intégration — appliquer 2× les migrations → même état.
Preuves : sortie `docker compose ps`, `\dn`.

**DE-001 — Acquisition et figeage du dataset** · Data Engineering · P0 · 0,5 j · DO-001
→ Téléchargement reproductible, vérifié par empreinte.
Tâches : `scripts/download_dataset` (URL officielle IBM, contrôle SHA-256, échec si différent), `data/README.md` (source, licence, date, empreinte).
CA : empreinte = `16320c9c…3055e91` ; un fichier altéré est rejeté.
Tests : unitaire du contrôle d'empreinte.

**RS-001 — Étude du dataset et dictionnaire de données** · Research · P0 · 0,75 j · DE-001
→ Connaître exactement les colonnes, types, modalités et anomalies.
Tâches : notebook/rapport de profilage (types, NA, modalités, distributions), `docs/data_dictionary.md` (source → staging, règle, type).
CA : les 21 colonnes documentées ; anomalies connues (11 `TotalCharges` vides, `SeniorCitizen` 0/1, modalités « No … service ») expliquées.
Preuves : `report_assets/eda/profiling_*.png`.

**DOC-S1 — Documentation sprint 1** · Documentation · P0 · 0,5 j · —
→ `project_charter.md`, `requirements.md` (FR/NFR tracés), `architecture.md` (diagramme MVP), `architecture_decisions.md` (ADR-001…), `weekly_progress.md` S1.

**REV-S1 — Bilan de sprint 1** · Documentation · P0 · 0,25 j · toutes S1
→ Démo courte, objectifs prévus vs réalisés, écarts, preuves, PR `develop → main`, tag `v0.1.0` après ta validation.

---

## Sprint 2 — Ingestion et premières transformations
**Livrable** : `cip pipeline ingest data/raw/telco.csv` charge 7 043 lignes en RAW, trace le lot, rejette un fichier non conforme ; STAGING alimenté.

**DB-002 — Tables de traçabilité `app.*`** · Database · P0 · 0,5 j · DB-001
→ `app.ingestion_run`, `app.quarantine_row` (contraintes CHECK du CDC).
CA : statut hors domaine refusé par la base.

**DE-002 — Validation de schéma (Pandera)** · Data Engineering · P0 · 1 j · RS-001
→ Refuser avant chargement un fichier mal formé.
Tâches : schéma Pandera (colonnes obligatoires, types attendus, domaines) ; contrôles fichier (extension, taille max, encodage UTF-8, en-tête) ; rapport d'erreurs structuré.
CA : colonne manquante → lot `FAILED` + diagnostic lisible ; colonne en trop → avertissement.
Tests : fixtures CSV (valide, colonne manquante, mauvais encodage, vide, doublons).

**DE-003 — Chargement RAW traçable et idempotent** · Data Engineering · P0 · 1 j · DE-002, DB-002
→ Copier fidèlement la source dans `raw.telco_customer` avec `ingestion_id`.
Tâches : `ingestion_run` RUNNING → SUCCESS/FAILED/PARTIAL ; compteurs `rows_read`/`rows_loaded` ; empreinte du fichier ; refus d'un re-chargement identique sauf `--force` ; transaction (tout ou rien).
CA : 7 043 lignes chargées ; relancer ne crée pas de doublon ; une erreur au milieu ne laisse pas de lot partiel non tracé.
Tests : intégration CSV → PostgreSQL ; test d'idempotence ; test d'échec simulé.
Preuves : requête de comptage + ligne `ingestion_run`.

**DE-004 — Transformation STAGING** · Data Engineering · P0 · 1 j · DE-003
→ Données typées, nommées et nettoyées, règles explicites.
Tâches : `transformations/sql/staging_customer.sql` ; snake_case ; `Yes/No` → BOOLEAN ; `SeniorCitizen` → BOOLEAN ; `TotalCharges` vide → NULL (tracé) ; trim ; `Churn` → `churn_label` 0/1 ; déduplication documentée.
CA : 7 043 lignes ; 11 `total_charges` NULL toutes à `tenure_months = 0` ; aucune ligne perdue sans trace.
Tests : unitaires de normalisation + intégration RAW → STAGING.

**BE-001 — Squelette FastAPI + `/health` + module ingestion** · Backend · P0 · 0,5 j · DE-003
→ Démarrer l'API tôt pour éviter le big-bang de S7.
Tâches : app factory, gestion centralisée des erreurs, `GET /health` (vérifie la DB), `POST /ingestions`, `GET /ingestions/{id}`.
Tests : TestClient (200, 404, 422).

**DOC-S2** · Documentation · P0 · 0,5 j → `etl_pipeline.md`, `database_design.md` (MCD/MLD), diagramme de séquence de l'ingestion, `weekly_progress.md`.
**REV-S2 — Bilan de sprint 2** · Documentation · P0 · 0,25 j.

---

## Sprint 3 — Data Quality, couche analytique, pipeline automatisé · Jalon M2
**Livrable** : `cip pipeline run` exécute ingest → quality → staging → analytics de bout en bout, avec rapport qualité historisé.

**DQ-001 — Moteur de règles qualité** · Data Engineering · P0 · 1 j · DE-004
→ Règles déclaratives exécutées en SQL, résultats dans `app.data_quality_result`.
Tâches : Q-01…Q-07 du CDC + complétude par colonne + fraîcheur du lot ; sévérité (`ERROR` bloque, `WARN` signale) ; mise en quarantaine.
CA : chaque règle produit `status`, `failed_rows`, `details_json` ; une règle `ERROR` en échec bloque la publication analytics.
Tests : fixtures provoquant chaque règle (id nul, doublon, montant négatif, churn hors domaine, catégorie inconnue).

**DQ-002 — Rapport qualité** · Data Engineering · P0 · 0,5 j · DQ-001
→ Rapport Markdown/HTML par lot dans `quality/reports/` + endpoint `GET /quality/{ingestion_id}`.
Preuves : rapport du lot de référence.

**DB-003 — Couche ANALYTICS et vues autorisées** · Database · P0 · 1 j · DE-004
→ `analytics.customer_snapshot`, `analytics.customer_features`, vues `v_churn_overview`, `v_churn_by_segment`, `v_customer_risk`.
CA : taux de churn de la vue = 26,5 % (cohérent avec le profilage) ; granularité documentée.
Tests : tests SQL de cohérence (sommes, comptes, unicité).

**DE-005 — Orchestrateur CLI** · Data Engineering · P0 · 0,75 j · DQ-001, DB-003
→ `cip pipeline run [--file] [--force]` : étapes ordonnées, arrêt sur erreur bloquante, journalisation, code de sortie.
CA : rejouable ; un échec qualité stoppe proprement avec statut tracé.
Tests : test du pipeline complet sur base de test.

**BE-002 — Endpoints analytics** · Backend · P0 · 0,5 j · DB-003 → `GET /analytics/overview`, `GET /customers/{id}`.

**DE-006 — dbt Core (si D4 = oui)** · Data Engineering · P1 · 2 j · DB-003 → Porter staging/analytics en modèles dbt + tests. *Abandonné si S3 en retard.*

**DOC-S3** · P0 · 0,5 j → `data_quality.md`, mise à jour `etl_pipeline.md`, diagramme de flux. **REV-S3** · P0 · 0,25 j · tag `v0.3.0`.

---

## Sprint 4 — EDA, feature engineering, baseline et comparaison
**Livrable** : rapport de comparaison de 3 modèles en validation croisée, tracé dans MLflow.

**ML-001 — EDA et analyse de la cible** · ML · P0 · 1 j · DB-003
→ Distributions, churn par segment, corrélations, déséquilibre (26,5 %), colinéarité `total_charges`/`tenure`, variables sensibles.
Livrables : notebook `notebooks/01_eda.ipynb` exporté + figures `report_assets/eda/` légendées.

**ML-002 — Split figé sans fuite** · ML · P0 · 0,5 j · ML-001
→ Train/val/test 60/20/20 stratifié, seed fixée, indices versionnés.
Tests : pas d'intersection entre ensembles ; proportions de churn similaires (±1 pt).

**ML-003 — Pipeline de préparation et features** · ML · P0 · 1 j · ML-002
→ `ColumnTransformer` (imputation, one-hot, scaling) + features métier (ex. nb de services, charge moyenne).
Tests : le pipeline n'est ajusté que sur train ; entrée avec catégorie inconnue gérée.

**DO-004 — Service MLflow** · DevOps · P0 · 0,25 j · DB-001 → Conteneur MLflow (backend Postgres, artefacts sur volume).

**ML-004 — Baseline et comparaison** · ML · P0 · 1,25 j · ML-003, DO-004
→ Dummy, LogReg, Random Forest, XGBoost ; CV stratifiée 5 plis sur train ; métriques : accuracy, precision, recall, F1, ROC-AUC, PR-AUC ; chaque run dans MLflow.
CA : tableau comparatif reproductible (même seed → mêmes chiffres).
Preuves : capture MLflow, tableau des métriques **réellement obtenues**.

**DOC-S4** · P0 · 0,5 j → `machine_learning.md`. **REV-S4** · P0 · 0,25 j.

---

## Sprint 5 — Optimisation, évaluation, SHAP, tracking · Jalon M3
**Livrable** : modèle sélectionné, évalué une fois sur le test, versionné, servi par `POST /predictions`, expliqué par SHAP.

**ML-005 — Optimisation raisonnable** · ML · P0 · 1 j · ML-004 → Recherche aléatoire bornée (≤ 50 essais) sur les 2 meilleurs candidats, gestion du déséquilibre (`class_weight` / `scale_pos_weight`).

**ML-006 — Choix du seuil et sélection** · ML · P0 · 0,75 j · ML-005
→ Courbe coût selon le seuil sur validation, hypothèse FN/FP (D8), sélection argumentée (pas sur l'accuracy).
Livrables : `model_evaluation.md` ; courbes ROC/PR, matrice de confusion.

**ML-007 — Évaluation finale et versionnement** · ML · P0 · 0,5 j · ML-006
→ Évaluation unique sur le test ; enregistrement dans `app.model_run` + MLflow Model Registry ; model card.

**ML-008 — Service d'inférence + endpoints** · Backend · P0 · 0,75 j · ML-007
→ `POST /predictions` (1 ou n clients), bandes de risque LOW/MEDIUM/HIGH, historisation dans `app.prediction`, `GET /models/active`.
Tests : schéma d'entrée invalide → 422 ; probabilité ∈ [0,1] ; prédiction rattachée à `run_id`.

**XAI-001 — SHAP global et local** · ML · P0 · 1 j · ML-007
→ Importance globale (beeswarm/bar), explication d'un client (waterfall), `GET /explanations/{prediction_id}`.
CA : la somme des contributions + valeur de base = sortie du modèle (contrôle numérique) ; libellés « facteurs du modèle », pas « causes ».

**ML-009 — Analyse d'équité simple** · ML · P1 · 0,5 j → Écarts de recall par `gender` / `senior_citizen`, décision documentée.

**DOC-S5** · P0 · 0,5 j → `explainable_ai.md`, `model_evaluation.md`. **REV-S5** · tag `v0.5.0` · **point Go/No-Go des P1**.

---

## Sprint 6 — Generative AI · Jalon M4
**Livrable** : l'assistant répond à un jeu de questions de test : chiffres via SQL contrôlé, définitions via RAG avec sources, abstention hors périmètre, requêtes dangereuses bloquées.

**AI-001 — Adaptateur LLM + mode mock** · GenAI · P0 · 0,5 j · DO-003
→ Interface `LLMClient`, implémentation réelle (fournisseur D5, clé via `.env`) et mock déterministe ; timeouts, retries, journalisation sans secret.
CA : toute la suite de tests passe sans clé.

**AI-002 — Corpus documentaire approuvé** · GenAI · P0 · 0,5 j · DOC-S5
→ Dictionnaire, définitions KPI, règles qualité, model card, guide de fidélisation (marqué « indicatif »).

**AI-003 — Indexation RAG** · GenAI · P0 · 0,75 j · AI-002
→ Découpage par section avec métadonnées, embeddings multilingues locaux, index FAISS persisté, commande `cip rag build`.

**AI-004 — Réponse RAG avec citations et abstention** · GenAI · P0 · 0,75 j · AI-003, AI-001
→ Seuil de similarité ; prompt « réponds uniquement à partir du contexte » ; sources affichées ; abstention si aucun passage pertinent.
Tests : 10 questions de référence (retrieval@k), 3 questions hors corpus → abstention.

**DB-004 — Rôle PostgreSQL read-only** · Database · P0 · 0,25 j · DB-003
→ `cip_assistant` : `SELECT` uniquement sur `analytics.v_*`, `default_transaction_read_only`, `statement_timeout`.
Tests : `INSERT`/`DROP` avec ce rôle → refus de la base (défense indépendante du code).

**AI-005 — Text-to-SQL sécurisé** · GenAI · P0 · 1,25 j · DB-004, AI-001
→ Prompt avec schéma des vues ; validation **sqlglot** (une seule instruction, `SELECT` uniquement, tables dans la liste blanche, pas de fonctions dangereuses) ; `LIMIT` forcé ; exécution avec rôle read-only ; journalisation dans `app.assistant_interaction` ; formulation de la réponse à partir du résultat.
Tests : 20 questions de référence comparées à un SQL de référence ; suite d'attaques (DELETE, DROP, `;` multiples, `pg_sleep`, accès `app.*`, injection de prompt).

**AI-006 — Routeur et endpoint `/assistant/query`** · Backend · P0 · 0,5 j · AI-004, AI-005 → Modes `sql`, `rag`, `auto`.

**DOC-S6** · P0 · 0,5 j → `generative_ai.md` (architecture, garde-fous, limites des LLM, résultats d'évaluation réels). **REV-S6**.

---

## Sprint 7 — Interface, intégration, Docker · Jalon M5
**Livrable** : parcours de démonstration complet dans Streamlit, toute la plateforme démarre avec `docker compose up`.

**UI-001 — Squelette Streamlit + client API + Accueil** · Frontend · P0 · 0,5 j → Client HTTP unique, gestion d'erreurs API, page d'accueil (état des services, dernier lot).
**UI-002 — Pages Qualité et Exécutions** · Frontend · P0 · 0,5 j.
**UI-003 — Page Analytics** · Frontend · P0 · 0,75 j → KPI, segments, distributions.
**UI-004 — Pages Risque client et Model Insights / SHAP** · Frontend · P0 · 1 j.
**UI-005 — Page Assistant IA** · Frontend · P0 · 0,75 j → Chat, mode, sources, SQL exécuté visible.
**UI-006 — Upload CSV depuis l'UI** · Frontend · P1 · 0,5 j.
**DO-005 — Dockerisation complète** · DevOps · P0 · 0,75 j → Dockerfiles api/frontend (multi-stage, utilisateur non-root), compose avec healthchecks et dépendances, démarrage depuis un clone propre.
**BE-003 — Clé API sur endpoints admin** · Backend · P1 · 0,25 j.
**DOC-S7** · P0 · 0,5 j → `user_guide.md` (captures), `api_documentation.md`. **REV-S7** · tag `v0.7.0`.

---

## Sprint 8 — Tests finaux, CI/CD, rapport, soutenance · Jalon M6
**Livrable** : version `v1.0.0` reproductible, tests verts, documentation et support de soutenance prêts.

**QA-001 — Test E2E du scénario de démo** · Backend · P0 · 1 j → Upload → pipeline → analytics → prédiction → explication → assistant, automatisé.
**QA-002 — Couverture et scénarios d'erreur** · Backend · P0 · 0,5 j → Couverture mesurée (objectif ≥ 70 % sur `src/`), cas d'erreur du §15.1 du CDC.
**DO-006 — CI complète** · DevOps · P0 · 0,5 j → Service Postgres en CI, tests d'intégration, build des images, badge README.
**DO-007 — Installation depuis zéro sous Windows** · DevOps · P0 · 0,25 j → Validation de `deployment_guide.md` sur machine propre.
**DOC-001 — Finalisation `docs/`** · Documentation · P0 · 1 j → `testing_strategy.md`, `deployment_guide.md`, `technical_challenges.md`, `limitations_and_future_work.md`, `bibliography.md`.
**DOC-002 — Rapport PFA et slides** · Documentation · P0 · 1 j (+ travail continu).
**DOC-003 — Questions du jury et répétition** · Documentation · P0 · 0,5 j.
**REV-S8 — Bilan final + release `v1.0.0`** · P0 · 0,25 j.

**Optionnels (P2, uniquement si M5 atteint en avance)** : `DE-007 Airflow DAG` (2–3 j), `ML-010 Détection de dérive` (1,5 j), `DO-008 Déploiement cloud` (1–2 j).

---

## Récapitulatif de charge (P0 uniquement)

| Sprint | Charge P0 (j) | Marge sur 5 j |
|---|---|---|
| S1 | 5,0 | 0 (dont ~1 j de doc/cadrage) |
| S2 | 4,75 | 0,25 |
| S3 | 4,5 | 0,5 |
| S4 | 4,75 | 0,25 |
| S5 | 5,25 | −0,25 → couvert par P1 reportées |
| S6 | 5,25 | −0,25 → à surveiller (risque R1/R4) |
| S7 | 5,0 | 0 |
| S8 | 5,0 | 0 |

S5 et S6 sont les sprints les plus chargés : c'est pourquoi les P1 sont soumises à un Go/No-Go en fin de S5.
