# Journal d'avancement hebdomadaire

Chaque semaine : objectifs, réalisations vérifiables, choix, problèmes et solutions, tests, résultats, preuves, reste à faire.

---

## Sprint 1 — du 16/11 au 20/11/2026 · Cadrage, socle, dataset

> **Mise à jour du lundi 16/11 (jour 1).** Le sprint est en cours ; ce bilan sera complété le 20/11 (carte REV-S1).

### 1. Objectifs prévus
Cadrage validé ; dépôt et CI opérationnels ; configuration et logs ; PostgreSQL avec les 4 couches ; dataset figé et profilé ; documentation initiale.

### 2. Tâches réalisées (toutes fusionnées dans `develop`, CI verte)

| Carte | Réalisation | PR |
|---|---|---|
| PM-001 | Cadrage, audit de faisabilité, backlog de 8 sprints ; décisions validées par l'étudiante | — (validation encadrant en attente) |
| PM-002 | Tableau Trello : 8 listes, 70 cartes | — (labels à créer manuellement) |
| DO-001 | Dépôt, arborescence, conventions, licence | [#1](https://github.com/ouardifatimazohra/ai-customer-intelligence-platform/pull/1) |
| DO-002 | Ruff, Pytest, pre-commit, CI Linux + Windows | [#2](https://github.com/ouardifatimazohra/ai-customer-intelligence-platform/pull/2) |
| DO-003 | Configuration centralisée, logs par lot, masquage des secrets | [#5](https://github.com/ouardifatimazohra/ai-customer-intelligence-platform/pull/5) |
| DE-001 | Téléchargement vérifié par SHA-256, commandes `cip data` | [#6](https://github.com/ouardifatimazohra/ai-customer-intelligence-platform/pull/6) |
| DB-001 | PostgreSQL 16.16 (Docker Compose), migrations versionnées, CI d'intégration | [#7](https://github.com/ouardifatimazohra/ai-customer-intelligence-platform/pull/7) |
| RS-001 | Profilage calculé, figures, dictionnaire de données | [#8](https://github.com/ouardifatimazohra/ai-customer-intelligence-platform/pull/8) |
| DOC-S1 | Charte, exigences, architecture, ADR, difficultés, preuves | ce document |

### 3. Choix techniques et justification
- **uv + Python 3.12** : dépendances verrouillées, installation identique sous Linux, Windows et en CI (ADR-007).
- **CI sous Windows** : prouve la compatibilité avec le poste de l'étudiante sans installation locale (ADR-009).
- **Migrations SQL maison** plutôt qu'Alembic : simple, lisible, testé contre un vrai PostgreSQL (ADR-012).
- **Dataset figé par SHA-256** : reproductibilité des résultats (ADR-001).
- **Pas d'Airflow au MVP** : surdimensionné pour 5 étapes à la demande (ADR-003).

### 4. Problèmes rencontrés et solutions
Six problèmes réels, détaillés dans [`technical_challenges.md`](technical_challenges.md). Les deux plus significatifs :
- Les migrations ne s'appliquaient pas à cause de l'*autobegin* de SQLAlchemy 2 ; le bug a été trouvé par les tests d'intégration.
- `TotalCharges` contient des espaces (et non des vides) pour exactement les 11 clients à 0 mois d'ancienneté.

### 5. Tests effectués (résultats réels)
| Niveau | Résultat |
|---|---|
| Unitaires | 37 passés |
| Intégration PostgreSQL | 5 passés (en local et en CI) |
| Réseau (téléchargement réel) | 1 passé, en local |
| CI | 4 jobs verts sur la dernière PR (lint, Linux, Windows, intégration) |
| Démonstration d'échec | Une erreur de lint volontaire bloque la CI (PR #3, fermée) |

### 6. Résultats obtenus
- Dataset : 7 043 clients, 21 colonnes, 0 doublon, taux de churn 26,54 %.
- Base : 4 schémas créés ; un deuxième `cip db migrate` ne change rien.
- 8 PR fusionnées, 0 secret versionné.

### 7. Preuves conservées
Voir l'index [`report_assets/README.md`](../report_assets/README.md) : captures de la CI (verte et rouge), historique Git, PR, extraits d'exécution (logs, téléchargement, migrations), figures de profilage, diagramme d'architecture.

### 8. Reste à faire dans le sprint
- [ ] Validation encadrant : licence du dataset (D1) et périmètre (D2)
- [ ] Décision D10 : date de début réelle et jours non travaillés
- [ ] Labels Trello (création manuelle requise) et capture du tableau
- [ ] REV-S1 : démonstration, bilan final, PR `develop → main`, tag `v0.1.0` après validation
