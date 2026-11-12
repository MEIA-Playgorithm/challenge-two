# Data guide

All the data is in `data/csv/`, one folder per source. Everything is CSV and there are no repeated rows.
For sizes, row counts, columns and missing values, see the notebook `notebooks/01_data_overview.ipynb`.

## Summary

| Folder | What it has | Period | Size |
|---|---|---|---|
| `kaggle_eoinamoore_historical_nba` | Games, player and team stats per game, play-by-play, schedules | 1946 – Nov 2026 | 6.7 GB |
| `kaggle_wyattowalsh_basketball` | Games, play-by-play, draft, players, teams, officials | 1946 – Jun 2023 | 2.2 GB |
| `kaggle_nathanlauga_nba_games` | Games, player stats per game, daily standings | 2003 – Dec 2022 | 113 MB |
| `sportsdataverse_injuries` | Official injury reports | Dec 2018 – Nov 2026 | 238 MB |
| `boxscorelab` | Season summaries: players, team results, standings | 2022-23 – 2026-27 | 2 MB |

## Where to find what

| Looking for… | Recommended file | Alternatives |
|---|---|---|
| Result of each game | `eoinamoore/Games.csv` | `wyattowalsh/game.csv`, `nathanlauga/games.csv` |
| Each team's stats in each game | `eoinamoore/TeamStatistics.csv` | `wyattowalsh/game.csv` (home and away on the same row) |
| Each player's stats in each game | `eoinamoore/PlayerStatistics.csv` | `nathanlauga/games_details.csv` |
| Advanced stats (per game) | `eoinamoore/*Extended.csv` | — |
| Play-by-play | `eoinamoore/PlayByPlay.csv` (with x/y shot coordinates) | `wyattowalsh/play_by_play.csv` |
| Points per period (quarters) | `wyattowalsh/line_score.csv` | — |
| Points in the paint, fast breaks, lead changes | `wyattowalsh/other_stats.csv` | — |
| Injuries and absences | `sportsdataverse_injuries/injury_report_*.csv` | `wyattowalsh/inactive_players.csv` |
| Players' physical data | `eoinamoore/Players.csv` | `wyattowalsh/common_player_info.csv`, `wyattowalsh/draft_combine_stats.csv` |
| Draft | `wyattowalsh/draft_history.csv` | `eoinamoore/Players.csv` |
| Standings over the season | `nathanlauga/ranking.csv` | `boxscorelab/*-team-standings.csv` (final only) |
| Upcoming games schedule | `eoinamoore/LeagueSchedule26_27.csv` | — |
| Officials of each game | `wyattowalsh/officials.csv` | `eoinamoore/Games.csv` (`officials` column) |
| Attendance and arena | `eoinamoore/Games.csv` | `wyattowalsh/game_info.csv` |

## How to join the files

The sources use the official NBA IDs, so files from different sources can be joined. Only the column name changes:

| ID | eoinamoore | wyattowalsh | nathanlauga | sportsdataverse |
|---|---|---|---|---|
| Game | `gameId` | `game_id` | `GAME_ID` | `game_id` |
| Player | `personId` | `person_id`, `player_id`, `player1_id`… | `PLAYER_ID` | `person_id` |
| Team | `teamId`, `hometeamId`, `awayteamId` | `team_id`, `team_id_home`, `team_id_away` | `TEAM_ID`, `HOME_TEAM_ID` | `team_id` |

It has not yet been checked whether the IDs actually match across sources. boxscorelab has no IDs, only team names and abbreviations.

---

## kaggle_eoinamoore_historical_nba

The most complete and most up-to-date source: it goes up to the current season.
It includes regular season, playoffs, preseason, play-in, NBA Cup and All-Star (`gameType` column).

| File | One row is… | Rows | Period |
|---|---|---|---|
| `Games.csv` | a game (result, arena, attendance, officials) | 73,507 | 1946 – 2026 |
| `TeamStatistics.csv` | a team in a game (basic stats) | 147,016 | 1946 – 2026 |
| `TeamStatisticsExtended.csv` | a team in a game (104 columns, includes advanced) | 80,180 | 1996 – 2026 |
| `PlayerStatistics.csv` | a player in a game (basic stats) | 1,677,321 | 1946 – 2026 |
| `PlayerStatisticsExtended.csv` | a player in a game (110 columns, includes advanced) | 844,433 | 1996 – 2026 |
| `PlayByPlay.csv` | a game event (shot, foul, substitution…) | 18,864,106 | 1996 – Apr 2026 |
| `Players.csv` | a player (birth, height, weight, position, draft) | 6,820 | — |
| `TeamHistories.csv` | a period of a franchise (city and name) | 140 | — |
| `LeagueSchedule24_25.csv`, `25_26`, `26_27` | a scheduled game | ~1,300–1,400 each | one season each |

## kaggle_wyattowalsh_basketball

Historical NBA database, one table per file. It ends with the 2023 finals.
The dataset's CSV and SQLite versions were merged (see `README.md`).

| File | One row is… | Rows | Period |
|---|---|---|---|
| `game.csv` | a game, with both teams' stats | 65,698 | 1946 – 2023 |
| `game_summary.csv` | a game (status, TV broadcast) | 58,070 | 1946 – 2023 |
| `game_info.csv` | a game (attendance, duration) | 58,013 | 1946 – 2023 |
| `line_score.csv` | a game (points per quarter and overtime) | 58,013 | 1946 – 2023 |
| `other_stats.csv` | a game (points in the paint, second chance, leads) | 28,261 | — |
| `play_by_play.csv` | a game event | 13,585,539 | 1996 – 2023 |
| `inactive_players.csv` | an inactive player in a game | 110,184 | — |
| `officials.csv` | an official in a game | 70,941 | — |
| `common_player_info.csv` | a player (personal and career data) | 4,683 | — |
| `player.csv` | a player (name, whether active) | 4,836 | — |
| `draft_history.csv` | a draft pick | 8,257 | 1947 – 2023 |
| `draft_combine_stats.csv` | a player at the draft combine (body measurements and tests) | 1,633 | 2000 – 2023 |
| `team.csv`, `team_details.csv` | a team (city, arena, owner, coach) | 30 | current |
| `team_history.csv` | a period of a franchise | 60 | — |
| `team_info_common.csv` | **empty** (header only) | 0 | — |

## kaggle_nathanlauga_nba_games

A smaller, simpler dataset, from 2003 to 2022.

| File | One row is… | Rows | Period |
|---|---|---|---|
| `games.csv` | a game (points, percentages, whether the home team won) | 26,651 | 2003 – 2022 |
| `games_details.csv` | a player in a game | 668,628 | 2003 – 2022 |
| `ranking.csv` | a team on a given day (wins, losses, win %) | 210,342 | 2003 – 2022 |
| `players.csv` | a player on a team in a season | 7,228 | 2009 – 2019 |
| `teams.csv` | a team | 30 | — |

## sportsdataverse_injuries

Official NBA injury reports, one file per season (the year is the season's end year).
The NBA publishes several reports a day, so the same player appears many times for the same game.

| File | One row is… | Rows | Period |
|---|---|---|---|
| `injury_report_2019.csv` … `injury_report_2027.csv` | a player in a report (status, reason) | 1,347,766 in total | Dec 2018 – Nov 2026 |

Main columns: `game_date`, `team`, `report_player_name`, `current_status` (e.g. Out, Questionable), `reason`, `game_id` and `person_id`.

## boxscorelab

Ready-to-use summaries, three files per season, from 2022-23 to 2026-27 (2026-27 is still in progress).

| File | One row is… | Rows per season |
|---|---|---|
| `<season>-team-game-results.csv` | a team in a game (includes estimated offensive and defensive ratings) | 2,460 |
| `<season>-player-season-totals.csv` | a player in the season (totals, averages, TS%, usage) | ~460–580 |
| `<season>-team-standings.csv` | a team in the season (wins, net rating, pace, SOS) | 30 |

---

## Notes

- **Overlap:** the three Kaggle datasets cover many of the same games. To get started, **eoinamoore** is the best starting point, since it is the most complete and most up to date.
- **Older games:** before 1996 there are fewer stats (no play-by-play and many empty fields).
- **Current season:** the 2026-27 files only have the games played up to the download (mid-November 2026).
- **License:** the wyattowalsh dataset is CC-BY-SA-4.0, so the source must be cited if it is used in the report.
