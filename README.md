<p align="center">
  <img src="docs/assets/playgorithm-logo.png" alt="Playgorithm logo" width="200">
</p>

# challenge-two

We use NBA (National Basketball Association) data to build prediction models and test search algorithms such as A*. This is an academic machine learning project.

To find out what each data file contains, read the [data guide](docs/DATA_GUIDE.md).

## What is in this repository

```
data/archive/             the data, zipped and split into 95 MB parts
data/unzip.sh, unzip.ps1  scripts that rebuild data/csv/ from data/archive/
data/csv/<source>/        the data as CSV files (created by the unzip scripts, not stored in git)
docs/DATA_GUIDE.md        what each data file contains
docs/assets/              images used in the docs, such as the team logo
notebooks/                analysis notebooks
```

The notebook `01_data_overview` shows file sizes, row and column counts, sample rows, missing values and the years each source covers.

## Get the data

Run one of these commands from the repository folder after you clone it:

```bash
sh data/unzip.sh
```

```powershell
pwsh data/unzip.ps1
```

The script creates `data/csv/` in about 2 minutes. Git ignores that folder.

We store the data as a zip file because the CSV files take up about 9 GB, and GitHub rejects any file over 100 MB. The zip takes up 1.8 GB, split into 19 parts.

## Set up Python

Install the dependencies in a virtual environment inside the project, not in your global Python:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

To open the notebooks:

```bash
.venv/Scripts/python -m jupyter notebook notebooks/
```

## Data sources

| Folder in `data/csv/` | Source | Access |
|---|---|---|
| `kaggle_wyattowalsh_basketball` | https://www.kaggle.com/datasets/wyattowalsh/basketball (license: CC BY-SA 4.0) | Kaggle account required |
| `kaggle_nathanlauga_nba_games` | https://www.kaggle.com/datasets/nathanlauga/nba-games | Kaggle account required |
| `kaggle_eoinamoore_historical_nba` | https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores | Kaggle account required |
| `sportsdataverse_injuries` | https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/nba_stats_injury_report | Public (2019 to 2027) |
| `boxscorelab` | https://www.boxscorelab.com/downloads/ | Public (2022-23 to 2026-27) |

## How we prepared the data

We converted every source to CSV and removed duplicates without losing data:

- **Repeated rows:** We removed rows that appeared more than once in the same file, and kept the first copy.
- **wyattowalsh:** This dataset comes in two copies, a set of CSV files and a SQLite database. We merged each table into one CSV file.
  - The two copies write the same values in different ways: `12106.0` in one and `12106` in the other, and an empty text value in one and a blank field in the other. We treated these as equal.
  - Nine tables, including `game` and `play_by_play`, match in both copies.
  - `draft_history` and `draft_combine_stats`: The SQLite copy has every row of the CSV copy, plus more rows. We kept the SQLite copy.
  - `common_player_info`, `player`, `team`, `team_details` and `team_history`: When a record has the same ID but different values in the two copies, we kept the SQLite value. We also kept the records that exist only in the CSV copy. Each team has several rows in `team_history`, one for each period of its history.
  - The dataset also includes an empty DuckDB database file, which we did not keep.
- **eoinamoore:** We converted `PlayByPlay.parquet` to `PlayByPlay.csv`.
- **sportsdataverse:** We kept only the CSV files. The Parquet files in the same release hold the same rows and columns (we checked each year), and the RDS files hold the same data in the format used by the R language.
- **Overlap between sources:** The three Kaggle datasets cover many of the same games, with different column names. We kept them separate. We will combine them when we build the model features.

## Branches and commits

- **Branches:** `development` is the default branch and holds the latest finished work. `main` holds releases only. Make every change through a pull request: from your work branch into `development`, and from `development` into `main` for a release. Push only to your work branches. Name each work branch `type/task`, for example `docs/catalog-data`, `feature/thing` or `bugfix/thing`. Read the [branch guide](.claude/skills/branch-naming/SKILL.md).
- **Commits:** Write commit messages in English. Follow the NASA cFS (core Flight System) Git Commit Guidelines and the seven rules by Chris Beams, for example `Fix #12, Add data overview notebook`. Make one commit for each topic. Read the [commit guide](.claude/skills/commit/SKILL.md).
- **Documentation:** Write README and guide files in plain language, following the NASA writing standards. Read the [documentation guide](.claude/skills/docs-style/SKILL.md).
