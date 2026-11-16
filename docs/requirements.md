# Exigences

Source : cahier des charges technique v1.0. La colonne *Statut* reflète l'état **réel et vérifié** au 16/11/2026.
Légende : ✅ réalisé et vérifié · 🟡 partiellement réalisé · ⏳ prévu.

## Exigences fonctionnelles

| ID | Exigence | Priorité | Cartes | Statut |
|---|---|---|---|---|
| FR-01 | Importer un fichier CSV | Haute | DE-003, UI-006 | 🟡 acquisition du dataset source vérifiée (DE-001) ; import dans la base prévu en S2 |
| FR-02 | Valider le schéma | Haute | DE-002 | ⏳ S2 (le schéma réel est documenté : RS-001) |
| FR-03 | Tracer les lots | Haute | DB-002, DE-003 | 🟡 journalisation par identifiant de lot prête (DO-003) ; tables de lots prévues en S2 |
| FR-04 | Contrôler la qualité | Haute | DQ-001, DQ-002 | ⏳ S3 (règles de cohérence déjà identifiées et vérifiées au profilage) |
| FR-05 | Transformer les données | Haute | DE-004, DB-003 | ⏳ S2–S3 |
| FR-06 | Consulter les KPI | Haute | BE-002, UI-003 | ⏳ S3 / S7 |
| FR-07 | Entraîner et évaluer | Haute | ML-004 → ML-007 | ⏳ S4–S5 |
| FR-08 | Prédire le risque | Haute | ML-008 | ⏳ S5 |
| FR-09 | Expliquer une prédiction | Haute | XAI-001 | ⏳ S5 |
| FR-10 | Interroger les données (Text-to-SQL) | Haute | DB-004, AI-005 | ⏳ S6 |
| FR-11 | Interroger la documentation (RAG) | Moyenne | AI-002 → AI-004 | ⏳ S6 |
| FR-12 | Exposer une API | Haute | BE-001, BE-002, ML-008, AI-006 | ⏳ S2 → S6 |
| FR-13 | Historiser les interactions | Moyenne | AI-005 | ⏳ S6 |
| FR-14 | Consulter les exécutions | Moyenne | UI-002 | ⏳ S7 |

## Exigences non fonctionnelles

| ID | Exigence | Mise en œuvre | Statut |
|---|---|---|---|
| NFR-01 | Maintenabilité | Code par domaine (`src/cip/{data,db,...}`), configuration centralisée (`cip.config`), Ruff | ✅ socle en place |
| NFR-02 | Reproductibilité | Dépendances verrouillées (`uv.lock`), dataset figé par SHA-256, migrations versionnées | ✅ socle en place |
| NFR-03 | Qualité | Tests automatisés à chaque PR ; règles Data Quality en S3 | 🟡 |
| NFR-04 | Sécurité | Secrets en `SecretStr` et masqués dans les logs, `.env` bloqué par un hook pre-commit ; rôle SQL en lecture seule prévu en S6 | 🟡 |
| NFR-05 | Performance | Temps d'ingestion et de réponse à mesurer sur le dataset de démo | ⏳ S2 / S7 |
| NFR-06 | Observabilité | Logs ISO 8601 avec identifiant de lot (`cip.log`) | ✅ |
| NFR-07 | Accessibilité | Figures à teinte validée (contraste ≥ 3:1), libellés explicites | 🟡 |
| NFR-08 | Portabilité | Docker Compose ; CI sous Linux **et Windows** | 🟡 PostgreSQL conteneurisé ; API/UI en S7 |
| NFR-09 | Testabilité | 37 tests unitaires + 5 tests d'intégration PostgreSQL en CI | ✅ socle en place |
| NFR-10 | Fiabilité IA | Réponses chiffrées issues du SQL, citations RAG, abstention | ⏳ S6 |
