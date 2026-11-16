# Charte du projet

## Identité

| Champ | Valeur |
|---|---|
| Intitulé | AI-Powered Customer Intelligence Platform |
| Nature | Projet de fin d'année (PFA), cycle ingénieur informatique |
| Durée | 8 semaines — du 16/11/2026 au 08/01/2027 (date de début à confirmer, décision D10) |
| Étudiante | Ouardi Fatima Zohra |
| Cas d'usage | Prédiction et analyse du churn client (télécommunications) |
| Données | IBM Telco Customer Churn — 7 043 clients fictifs, 21 colonnes (voir [`data_dictionary.md`](data_dictionary.md)) |
| Contrainte | **100 % gratuit** : outils open source, offres gratuites uniquement |

## Problématique

Comment concevoir une plateforme intégrée qui transforme des données clients en informations fiables, prédit le risque de résiliation et permet aux utilisateurs métier d'interroger les résultats en langage naturel, tout en assurant traçabilité, sécurité et reproductibilité ?

## Objectifs

1. Chaîne de données reproductible et contrôlée : ingestion → qualité → couches RAW / STAGING / ANALYTICS (PostgreSQL).
2. Modèle de prédiction du churn évalué selon le coût métier des erreurs (et non la seule accuracy).
3. Explications des prédictions (SHAP), présentées comme des facteurs du modèle et non comme des causes.
4. Assistant IA : RAG documentaire avec citations et Text-to-SQL en lecture seule avec garde-fous.
5. API FastAPI et interface Streamlit démontrables.
6. Tests automatisés, CI, Docker Compose, documentation continue.

## Périmètre

- **MVP (obligatoire)**, **complémentaire** et **optionnel** : définis dans [`cadrage/00_cadrage_phase0.md`](cadrage/00_cadrage_phase0.md) §3 et validés (ADR-002).
- **Hors périmètre** : multi-tenant, Spark/Kafka, décisions automatiques sans validation humaine, données personnelles réelles, fine-tuning de LLM, haute disponibilité et Kubernetes.

## Jalons

| Jalon | Fin de | Condition de passage |
|---|---|---|
| M1 | S1 (20/11) | Architecture, dataset et périmètre validés ; environnement opérationnel |
| M2 | S3 (04/12) | Données dans le modèle analytique, qualité contrôlée |
| M3 | S5 (18/12) | Modèle évalué, versionné et explicable |
| M4 | S6 (25/12) | Assistant contrôlé sur un jeu de questions de test |
| M5 | S7 (31/12) | Parcours utilisateur intégré de bout en bout |
| M6 | S8 (08/01) | Installation reproductible, tests verts, démonstration prête |

## Outils de pilotage

- Tableau Trello : https://trello.com/b/tIeLvucF/ai-customer-intelligence-platform-pfa (privé)
- Dépôt : https://github.com/ouardifatimazohra/ai-customer-intelligence-platform
- Backlog de référence : [`cadrage/01_backlog_8_semaines.md`](cadrage/01_backlog_8_semaines.md)

## Règle de véracité

Tout résultat, métrique, capture ou fonctionnalité cité dans la documentation ou le rapport correspond à une réalisation vérifiable (commit, exécution de CI, fichier de preuve). Ce qui est seulement prévu est explicitement marqué « prévu ».
