-- 0001 — Couches logiques de données (DB-001)
--
-- raw       : copie fidèle des fichiers sources + métadonnées de chargement
-- staging   : données typées, nettoyées, normalisées
-- analytics : tables et vues prêtes pour l'analyse et le ML
-- app       : métadonnées applicatives (lots, qualité, modèles, prédictions, assistant)

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS app;

COMMENT ON SCHEMA raw IS 'Données sources brutes, jamais modifiées par les transformations';
COMMENT ON SCHEMA staging IS 'Données nettoyées et typées';
COMMENT ON SCHEMA analytics IS 'Modèle analytique et vues exposées (dont Text-to-SQL en lecture seule)';
COMMENT ON SCHEMA app IS 'Métadonnées applicatives et traçabilité';
