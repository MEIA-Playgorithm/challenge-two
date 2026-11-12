# challenge-two

Academic machine learning project on basketball (NBA): prediction models and search algorithms (e.g. A*).

**Data guide:** [docs/DATA_GUIDE.md](docs/DATA_GUIDE.md) lists what each file contains and where to find what.

## Structure

```
data/csv/<source>/        the data, CSV only, no duplicates (not in git)
docs/DATA_GUIDE.md        what each file contains
notebooks/                analysis notebooks (01_data_overview: sizes, rows, peeks, missing values, coverage)
```

The data itself is not in git (about 9 GB). It comes from the sources below and must be placed in `data/csv/<source>/` locally.

## Sources

| Folder in `data/csv/` | Source | Access |
|---|---|---|
| `kaggle_wyattowalsh_basketball` | https://www.kaggle.com/datasets/wyattowalsh/basketball (CC-BY-SA-4.0 license) | requires Kaggle login |
| `kaggle_nathanlauga_nba_games` | https://www.kaggle.com/datasets/nathanlauga/nba-games | requires Kaggle login |
| `kaggle_eoinamoore_historical_nba` | https://www.kaggle.com/datasets/eoinamoore/historical-nba-data-and-player-box-scores | requires Kaggle login |
| `sportsdataverse_injuries` | https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/nba_stats_injury_report | public (2019–2027) |
| `boxscorelab` | https://www.boxscorelab.com/downloads/ | public (2022-23 to 2026-27) |

## How data/csv/ was built

- **Repeated rows:** rows that are exactly identical within the same file were removed (the first one is kept).
- **wyattowalsh:** the data comes twice (CSV and `nba.sqlite`). Each table was merged into a single CSV. Before comparing, `12106.0` becomes `12106` and SQLite's empty text becomes blank, since these are only formatting differences.
  - 9 tables were identical in both versions, including `game` and `play_by_play`.
  - `draft_history` and `draft_combine_stats`: SQLite has everything the CSV has, plus more rows.
  - `common_player_info`, `player`, `team`, `team_details` and `team_history`: when the same record (same ID) has different values in the two versions, the SQLite one is kept. Records that only exist in the CSV are kept too. In `team_history` each team has several rows (one per period), which is expected.
  - `nba.duckdb` was empty.
- **eoinamoore:** `PlayByPlay.parquet` was converted to `PlayByPlay.csv`.
- **sportsdataverse:** only the `.csv` files. The release's `.parquet` files have the same rows and columns (checked year by year); the `.rds` files are the R format of the same data.
- **Overlap between datasets:** the three Kaggle datasets cover the same games with different schemas. They were not merged; that is left for the feature engineering phase.

## Setup

Dependencies live in a project virtual environment (`.venv`), not in the global Python.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

To open the notebooks:

```bash
.venv/Scripts/python -m jupyter notebook notebooks/
```

## Commits

Commit messages follow `type/task` (e.g. `docs/catalog-data`, `feature/data-overview-notebook`, `bugfix/null-count`). See [.claude/skills/commit-convention/SKILL.md](.claude/skills/commit-convention/SKILL.md).
