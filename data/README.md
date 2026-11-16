# Données

Aucune donnée n'est versionnée dans Git (`data/raw`, `data/interim`, `data/processed` sont ignorés).
Les fichiers sont téléchargés depuis leur source officielle et vérifiés par empreinte.

## Dataset source — IBM Telco Customer Churn

| Champ | Valeur |
|---|---|
| Nom | IBM Telco Customer Churn (jeu d'exemple, clients **fictifs**) |
| Source | `https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv` |
| Dépôt d'origine | https://github.com/IBM/telco-customer-churn-on-icp4d (organisation GitHub officielle d'IBM) |
| Licence | Apache License 2.0 (licence du dépôt ; IBM ne publie pas de licence distincte pour les données). Usage académique ; validation par l'encadrant demandée (décision D1). |
| Version figée (SHA-256) | `16320c9c1ec72448db59aa0a26a0b95401046bef5d02fd3aeb906448e3055e91` |
| Taille | 970 457 octets |
| Volume | 7 043 lignes, 21 colonnes (+ en-tête) |
| Fichier local | `data/raw/telco_customer_churn.csv` |
| Vérifiée le | 16/11/2026 |
| Données personnelles | Aucune (identifiants et clients fictifs) |

## Commandes

```powershell
uv run cip data download          # télécharge et vérifie (réutilise un fichier déjà conforme)
uv run cip data download --force  # retélécharge
uv run cip data verify            # contrôle l'empreinte du fichier local
```

Codes de sortie : `0` conforme · `1` fichier absent · `2` empreinte différente (fichier rejeté).

## Pourquoi une empreinte SHA-256 ?

Le fichier distant peut changer sans préavis. En figeant son empreinte, toute modification
(source mise à jour, téléchargement tronqué, fichier altéré localement) est détectée avant
l'ingestion : les résultats (qualité, modèles, métriques) restent reproductibles.
