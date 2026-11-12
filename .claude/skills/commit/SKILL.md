---
name: commit
description: Steps and message format for making commits in this project (NASA cFS Git Commit Guidelines + Chris Beams' seven rules). Use whenever the user asks to commit in the challenge-two repository. Never commit unless the user asks.
---

# Commit

## Before committing

1. **Only commit when the user asks.** Never commit on your own initiative, not even at the end of a task. If work is ready, say so and wait.
2. **Check the branch.** Run `git branch --show-current`.
   - Never commit to `development` or `main`.
   - Make sure the branch matches the work being committed. If it does not (or you are on `development`/`main`), stop and ask, or create a new branch following the `branch-naming` skill.
3. **Group the changes by topic.** Look at `git status` and `git diff`, and split the changes into one commit per topic (for example docs, a notebook, the data archive). Stage each group on its own (`git add <files>`), never `git add -A` blindly.
4. **Check what goes in.** No extracted CSVs (`data/csv/`), no `.venv/`, no files over 100 MB, no credentials or tokens.

## Message format

This project follows NASA's cFS **Git Commit Guidelines**, which build on Chris Beams' **The Seven Rules of a Great Git Commit Message**. Messages are in English.

```
Fix #XYZ, Short description

Optional longer description: what changed and why.
```

- `Fix #XYZ,` links the commit to a GitHub issue. Include it when the work has an issue; leave it out when there is none.

### The seven rules

1. Separate the subject from the body with a blank line.
2. Limit the subject line to 50 characters.
3. Capitalize the subject line.
4. Do not end the subject line with a period.
5. Use the imperative mood in the subject line ("Add", not "Added" or "Adds").
6. Wrap the body at 72 characters.
7. Use the body to explain what and why, not how.

A good subject completes the sentence: "If applied, this commit will _\<subject\>_".

## Examples

```
Fix #12, Add data overview notebook
```

```
Add unzip scripts for the data archive

The CSVs are too large for GitHub (files over 100 MB are rejected),
so they are stored as a zip split into 95 MB parts. These scripts
rebuild data/csv/ on Linux, macOS and Windows.
```

```
Fix #7, Count empty strings as missing values
```

## References

- NASA cFS Git Commit Guidelines: https://github.com/nasa/cFS/blob/main/CONTRIBUTING.md
- Chris Beams, How to Write a Git Commit Message: https://cbea.ms/git-commit/
