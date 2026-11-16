# Difficultés techniques et solutions

Chaque entrée décrit un problème **réellement rencontré**, sa cause, la solution et la preuve.

## S1-01 — Migrations jamais appliquées (SQLAlchemy 2, « autobegin »)
- **Symptôme** : `cip db migrate` échouait avec `InvalidRequestError: This connection has already initialized a SQLAlchemy Transaction()` ; aucun schéma créé.
- **Cause** : en SQLAlchemy 2, la première requête d'une connexion ouvre implicitement une transaction. La pose du verrou `pg_advisory_lock` ouvrait donc une transaction, et le `conn.begin()` suivant était refusé.
- **Solution** : `commit()` explicite juste après la pose du verrou, puis une transaction distincte par étape ; `rollback()` de sécurité avant de libérer le verrou.
- **Comment il a été détecté** : par les tests d'intégration contre un vrai PostgreSQL. Des tests avec une base simulée ne l'auraient pas vu.
- **Preuve** : PR #7, `report_assets/tests/S1_postgres_migrations_DB-001.txt`.

## S1-02 — `TotalCharges` : des valeurs « vides » qui n'en sont pas
- **Constat** : les 11 valeurs manquantes valent `" "` (un espace), pas une chaîne vide.
- **Risque** : un contrôle `valeur = ''` ne les détecte pas et une conversion numérique naïve échoue.
- **Solution** : détection par `TRIM(...) = ''` ; conversion en `NULL` tracée en STAGING. Les 11 lignes sont exactement les clients à `tenure = 0`, ce qui est vérifié automatiquement à chaque profilage.
- **Preuve** : PR #8, `report_assets/eda/profiling_summary.json` (`consistency`).

## S1-03 — Actions GitHub obsolètes (Node 20)
- **Symptôme** : avertissement de dépréciation de Node 20 pour `actions/checkout@v4` et `astral-sh/setup-uv@v6`.
- **Solution** : passage à `checkout@v5` et `setup-uv@v7`, dont l'exécution sous Node 24 a été vérifiée dans leur `action.yml`.
- **Preuve** : commit `dc49442`, run CI 43904273765 sans avertissement.

## S1-04 — Captures GitHub sans style
- **Symptôme** : captures automatiques rendues en HTML brut.
- **Cause** : le domaine `github.githubassets.com` était bloqué par la politique réseau de l'environnement cloud (HTTP 403 du proxy).
- **Solution** : environnement dédié au projet autorisant ce seul domaine, créé avec l'accord de l'étudiante.

## S1-05 — Limite de téléchargement Docker Hub (HTTP 429)
- **Symptôme** : `docker compose up` refusé par Docker Hub (trop de requêtes anonymes).
- **Solution** : l'image `postgres:16-alpine` déjà présente localement est exactement la version 16.16 (vérifié par `postgres --version`) ; elle a reçu le tag `16.16-alpine` localement. La CI GitHub télécharge l'image normalement.

## S1-06 — Ergonomie : traceback quand la base est arrêtée
- **Symptôme** : centaines de lignes de traceback si PostgreSQL n'est pas démarré.
- **Solution** : message d'erreur explicite et code de sortie 3, couverts par un test unitaire.

## S1-07 — Branche `develop` supprimée automatiquement à la release
- **Symptôme** : après la fusion de la PR `develop → main` (v0.1.0), la branche `develop` avait disparu de GitHub.
- **Cause** : l'option « Automatically delete head branches » supprime la branche source de toute PR fusionnée, y compris `develop`.
- **Solution** : `develop` recréée exactement au même commit (`bfc22d2`, second parent du commit de fusion de `main`), sans aucune perte. Désormais, les PR vers `main` partent d'une branche `release/*` (CONTRIBUTING.md).

## S1-08 — Tags et Releases réservés à l'étudiante
- **Constat** : l'environnement de développement de l'assistant ne peut ni pousser de tag ni créer de Release GitHub (restriction volontaire du proxy).
- **Décision** : ces actions de publication restent manuelles et sont faites par l'étudiante dans l'interface GitHub, ce qui garantit qu'aucune version n'est publiée sans elle.
