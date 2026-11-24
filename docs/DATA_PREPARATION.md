# Prepare the shared datasets

Run `python3 scripts/prepare_data.py` from the repository root to prepare the data for both machine learning tasks.
The script uses Python 3.11 or later and needs no third-party packages.
It reads the existing CSV collection and leaves the source files unchanged.

## Collect and reproduce the data

The repository already contains the source collection as split archives.
If `data/csv/` is missing, run `sh data/unzip.sh` first.
The [README](../README.md#data-sources) lists the original providers and their links.
The [data guide](DATA_GUIDE.md) describes the source files and their coverage.
Credit each provider in your report. The wyattowalsh collection uses CC BY-SA 4.0.

The preparation script inventories all CSV files, including their columns, sizes and modification times.
It records row counts and SHA-256 fingerprints for files it scans.
Files listed without `rows_scanned` were inventoried, but their contents were not profiled.
The script does not download a new snapshot or combine overlapping sources blindly.

```bash
python3 scripts/prepare_data.py
python3 -m unittest discover -s tests -v
```

To change the scope, provide the season start years and a new destination:

```bash
python3 scripts/prepare_data.py --start-season 2019 --end-season 2025 --output data/prepared
```

The destination must not exist. This prevents old outputs from mixing with a new run.
A completed run contains `_SUCCESS`. An interrupted run does not.
Keep successful outputs until you have reviewed any replacement.
The event file is large; preparation scans the source in order without loading it all into memory.
The script stores compact fingerprints to identify exact repeated events.
It uses a temporary SQLite index to audit repeated event identities.

## Scope and decisions

The default scope covers regular-season games from 2019–20 through 2025–26.
It excludes playoffs, preseason, All-Star games and games without valid final scores.
The primary source is `kaggle_eoinamoore_historical_nba`.
The `002` game ID prefix defines regular-season membership.
This includes Cup games with regular-season IDs, even when their label says `NBA Emirates Cup`.
Some source labels otherwise exclude 66 games from 2023–24.
A game labeled regular season with a different ID prefix goes to quarantine for review.
This excludes the Cup final with a `006` prefix.

NBA game IDs encode the season start year. We use that year instead of the calendar month.
This keeps delayed 2019–20 and 2020–21 games in their correct seasons.
The observed counts do not prove that every scheduled game is present.

We use CSV output so preparation runs without extra dependencies.
Empty fields remain missing values. We preserve zeros and source precision.
We do not replace missing statistics with zero or remove statistical outliers automatically.
An exceptional performance can be a valid observation.

## Output tables

| File | One row represents | Key or join rule |
| --- | --- | --- |
| `games.csv` | An accepted game, its result and chronological split | `game_id` |
| `team_games.csv` | A team in a game | `game_id`, `team_id` |
| `team_games_extended.csv` | Advanced statistics for a team in a game | `game_id`, `team_id` |
| `player_games.csv` | A player listed in a game | `game_id`, `player_id` |
| `player_games_extended.csv` | Advanced statistics for a player listed in a game | `game_id`, `player_id` |
| `players.csv` | A player referenced by accepted statistics | `player_id` |
| `injury_reports.csv` | A player observation in an injury report | Keep publication time and source row |
| `play_by_play.csv` | An accepted game event | `source_row` identifies its original CSV row |
| `event_coverage.csv` | Event count for each selected game | `game_id` |
| `event_key_conflicts.csv` | A repeated event identity requiring review | `game_id`, `period`, `action_number` |
| `source_game_matches.csv` | A game ID shared with a secondary source | Inspect date, team and score agreement |
| `source_player_matches.csv` | A player ID shared with wyattowalsh | Inspect name agreement |
| `repairs.csv` | An audited field repair | Source file, row and field |
| `quarantine.csv` | A rejected record, its original contents and reason | Source file and row |

Basic and extended statistics stay separate to preserve their different coverage.
Left-join extended data to basic data and validate a one-to-one relationship.
Join `players` to player statistics with a many-to-one relationship.
Missing biographies receive an ID-only row so the player remains in the dataset.
The quality report lists these missing biographies explicitly.

When using pandas, preserve identifiers as strings and validate joins:

```python
import pandas as pd

root = "data/processed/"
ids = {"game_id": "string", "team_id": "string", "player_id": "string"}
teams = pd.read_csv(root + "team_games.csv", dtype=ids)
advanced = pd.read_csv(root + "team_games_extended.csv", dtype=ids)
extra_columns = [c for c in advanced.columns if c not in teams.columns]
teams = teams.merge(
    advanced[["game_id", "team_id"] + extra_columns],
    on=["game_id", "team_id"], how="left", validate="one_to_one",
)
```

Import any other identifier columns as strings when you use them in joins.

Secondary game sources provide independent checks rather than replacement rows.
The audit checks dates, ordered home/away team IDs and final scores.
Player name differences are review flags, not evidence that two players are different people.
We do not merge the secondary biographies automatically.
Boxscorelab uses names rather than IDs and remains outside the common tables.

## Normalization and validation

- Convert column names to snake case and standardize game, player and team ID names.
- Store game IDs as 10-character strings, restoring leading zeros lost by numeric exports.
- Accept integer IDs written with a `.0` suffix. Reject other non-integer ID formats.
- Keep game timestamps as source text. Their timezone interpretation remains unverified.
- Convert `MM:SS` playing time to decimal minutes. Preserve existing decimal minutes.
- Add centimetres and kilograms to player biographies, retaining inches and pounds.
- Check game scores, winner consistency, opposing teams and season years.
- Check team membership, opponent IDs, home flags, team scores and made/attempted shot counts.
- Quarantine repeated business keys instead of arbitrarily choosing conflicting records.
- Preserve repeated injury publications. Remove only identical normalized injury observations.
- Remove only exact full-record event duplicates. Action numbers alone are not unique keys.

Some player rows have missing team IDs but retain team names and a home/away flag.
We repair a missing ID only when the flag and both city/name pairs match the game record.
Each accepted field repair appears in `repairs.csv`. We do not overwrite populated IDs.

Player statistics include `participation_status`: `played`, `zero_minutes` or `unknown`.
Zero minutes alone does not establish the reason for an absence.
Do not treat all listed players as participants when calculating per-minute performance.

## Read the quality report

Each completed run writes:

- `QUALITY_REPORT.md`: readable counts, validation findings and limitations.
- `quality_report.json`: input inventory, fingerprints, checks and missing counts for every output column.
- `data_dictionary.csv`: columns, storage format, missing counts and normalization notes.
- `quarantine.csv`: source records that require review before use.

The dictionary documents the preparation contract. Original statistical definitions remain with the providers.
Review missing team rows, missing advanced statistics and event coverage before selecting model samples.
A successful run means preparation finished; it does not mean every source record passed validation.

## Hand over to Element 2

Start with `games.csv` and join team statistics through `game_id` and `team_id`.
The default `split` assigns 2019–20 through 2023–24 to training, 2024–25 to validation,
and 2025–26 to testing. Sort by game time before calculating histories.
For a custom scope, the final season becomes test and the preceding season becomes validation.

`home_win` is the target: 1 for a home win, otherwise 0.
Scores, attendance, winners, box scores and advanced statistics describe the completed game.
They are not automatically available before tip-off.
Build rolling statistics from earlier games and shift them before joining the prediction row.
Fit imputation and scaling on training data only.

Injury report publication times do not carry a verified timezone in this preparation.
All accepted publications remain in `injury_reports.csv`; no pregame snapshot is supplied.
Confirm the report and game timezones before selecting the latest report before the prediction cutoff.
An absent report does not establish that a player was healthy or available.

## Hand over to Element 3

Start with player statistics and the player dimension.
Use minutes and `participation_status` when selecting performance observations.
Biographical measurements are source snapshots, not measurements recorded before each historical game.

The event output retains descriptions, substitutions, player IDs, period clocks and source row numbers.
`clock_seconds_remaining` expresses time remaining in that period.
Rows retain source order, which is not globally chronological.
Group by game and check numeric event order, period and clock before building intervals.
Keep events at the same clock time in their recorded event order.
Event coverage varies across games and seasons.
The identity audit flags repeated game/period/action-number combinations.
Source versions can differ even when they describe the same event.
Resolve these collisions before counting events or reconstructing lineups.
The script prepares events; it does not certify or reconstruct five-player lineups.
Check starters, substitutions and period boundaries before computing lineup intervals.
Do not infer a full lineup merely from players mentioned in scoring events.

## Tests

The test fixture checks leading-zero joins, chronological splits, missing biographies and invalid team membership.
It also checks repeated publications, exact event duplicates and distinct events with the same action number.
It confirms that the pipeline refuses to overwrite an existing output directory.
