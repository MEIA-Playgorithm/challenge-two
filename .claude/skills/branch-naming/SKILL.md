---
name: branch-naming
description: Branch naming convention for this project (type/task, for example docs/catalog-data). Use whenever creating or naming a branch in the challenge-two repository.
---

# Branch naming convention

Branch names follow this format:

```
type/task
```

Never commit directly to `development` or `main`: create a branch from `development` and open a pull request back into it.

## Types

| Type | When to use |
|---|---|
| `docs` | Documentation: README, guides, data catalog |
| `feature` | New functionality: notebooks, models, algorithms, data features |
| `bugfix` | Fixing an error |

## Task

- A short description of the work on the branch.
- Lowercase, words separated by hyphens (kebab-case).
- No spaces, accents or punctuation.
- Keep it short: 2 to 5 words.

## Examples

```
docs/catalog-data
feature/thing
bugfix/thing
feature/game-prediction-model
bugfix/null-count
```

## Creating a branch

```bash
git switch development
git pull
git switch -c type/task
```

If no type fits, ask before inventing a new one.
