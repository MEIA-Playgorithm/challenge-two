---
name: branch-naming
description: Branch workflow and naming convention for this project (development is the default branch, main holds releases, all changes go through pull requests, branches are named type/task). Use whenever creating, naming, pushing or merging a branch in the challenge-two repository.
---

# Branches

## How the branches work

| Branch | What it is for | How changes get in |
|---|---|---|
| `development` | The default branch. It holds the latest finished work. | Pull request from a work branch |
| `main` | Releases only. | Pull request from `development` |
| Work branches (`type/task`) | One piece of work each. | Commits and pushes |

Follow these rules:

1. Make every change through a pull request, including changes to `development` and the release from `development` to `main`.
2. Push only to work branches. Never push to `development` or `main`.
3. Start every work branch from `development`, and open its pull request back into `development`.

## Name a work branch

Name each work branch in this format:

```
type/task
```

| Type | When to use |
|---|---|
| `docs` | Documentation: README, guides, data catalog |
| `feature` | New functionality: notebooks, models, algorithms, data features |
| `bugfix` | Fixing an error |

For the task part:

- Describe the work on the branch in 2 to 5 words.
- Use lowercase words separated by hyphens (kebab-case).
- Leave out spaces, accents and punctuation.

Examples:

```
docs/catalog-data
feature/thing
bugfix/thing
feature/game-prediction-model
bugfix/null-count
```

If no type fits, ask before you invent a new one.

## Create a work branch

```bash
git switch development
git pull
git switch -c type/task
```

## Release to main

When `development` is ready for a release, open a pull request from `development` into `main`.
