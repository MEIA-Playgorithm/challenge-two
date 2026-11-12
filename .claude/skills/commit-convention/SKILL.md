---
name: commit-convention
description: Commit message convention for this project (type/task, e.g. docs/catalog-data). Use whenever writing a commit message or making a commit in the challenge-two repository.
---

# Commit convention

The first line of a commit message follows this format:

```
type/task
```

## Types

| Type | When to use |
|---|---|
| `docs` | Documentation: README, guides, comments, reports |
| `feature` | New functionality: scripts, models, algorithms, data features |
| `bugfix` | Fixing an error |

## Task

- A short description of what was done.
- Lowercase, words separated by hyphens (kebab-case).
- No spaces, accents or punctuation.
- Keep it short: 2 to 5 words.

## Examples

```
docs/catalog-data
docs/data-guide
feature/data-overview-notebook
bugfix/null-count
```

## Body (optional)

After the first line, leave a blank line. Then explain why the change was made, in short sentences:

```
bugfix/null-count

Empty strings were not counted as missing values, so the null
percentages in the overview notebook were too low.
```

## Rules

- One commit per logical change. If a change spans two types (e.g. code and its documentation), use the main type.
- If no type fits, ask before inventing a new one.
