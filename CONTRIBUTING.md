# Conventions de travail

## Branches

| Branche | Rôle | Fusion |
|---|---|---|
| `main` | Versions stables et démontrables, une par fin de sprint, taguées `vX.Y.Z` | Uniquement depuis une branche `release/*`, après validation explicite |
| `develop` | Intégration des fonctionnalités | Via Pull Request, CI verte |
| `feature/<ID>-<slug>` | Une carte Trello = une branche (ex. `feature/DE-003-raw-ingestion`) | PR vers `develop` |
| `fix/<ID>-<slug>` | Correction ciblée | PR vers `develop` |
| `docs/<slug>` | Documentation seule | PR vers `develop` |
| `release/vX.Y.Z` | Préparation d'une version | PR vers `develop`, puis vers `main` |

On ne committe jamais directement sur `main` ni sur `develop`.

### Publier une version (fin de sprint)

1. Branche `release/vX.Y.Z` créée depuis `develop` : version passée à `X.Y.Z` dans `pyproject.toml` et `src/cip/__init__.py`, CHANGELOG daté.
2. PR `release/vX.Y.Z → develop`, puis PR **`release/vX.Y.Z → main`** après validation de l'étudiante.
   La PR vers `main` part de la branche `release/*` et **jamais de `develop`** : l'option GitHub « supprimer automatiquement les branches fusionnées » supprimerait sinon `develop`.
3. Après la fusion dans `main`, l'étudiante crée le tag et la Release depuis l'interface GitHub (*Releases → Draft a new release*, tag `vX.Y.Z`, cible `main`).

## Messages de commit — Conventional Commits

```
<type>(<scope>): <résumé à l'impératif, ≤ 72 caractères>

<corps : pourquoi ce changement, choix techniques>

Refs: <ID carte Trello>
```

- **types** : `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `perf`
- **scopes** : `data`, `db`, `quality`, `pipeline`, `ml`, `xai`, `genai`, `api`, `ui`, `infra`, `ci`, `docs`, `repo`

Exemple : `feat(data): implement raw customer data ingestion`

## Versions

[SemVer](https://semver.org/lang/fr/) : `v0.<sprint>.0` à chaque fin de sprint fusionnée dans `main`, `v1.0.0` pour la livraison finale. Les changements sont consignés dans [CHANGELOG.md](CHANGELOG.md).

## Definition of Done (toute carte)

1. Code fusionné dans `develop` via une PR.
2. CI verte (lint + tests).
3. Tests pertinents ajoutés et réussis.
4. Documentation `docs/` mise à jour.
5. Preuves rangées dans `report_assets/` (nom explicite + légende).
6. Carte Trello à jour : branche, commit(s), PR, statut réel.

## Règles de sécurité

- Jamais de secret, clé API, mot de passe, donnée ni environnement virtuel dans Git.
- Vérifier avant chaque commit : `git status` et `git diff --cached --stat`.
