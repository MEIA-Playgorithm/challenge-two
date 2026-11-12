# Data guide

Use this guide to find the right file for your analysis. All data files are CSV files in `data/csv/`, with one folder for each source. No file contains repeated rows.

To see file sizes, row counts, columns and missing values, open the notebook `notebooks/01_data_overview.ipynb`.

## Sources at a glance

| Folder | Contents | Period | Size |
|---|---|---|---|
| `kaggle_eoinamoore_historical_nba` | Games, team and player statistics for each game, play-by-play, schedules | 1946 to November 2026 | 6.7 GB |
| `kaggle_wyattowalsh_basketball` | Games, play-by-play, draft, players, teams, referees | 1946 to June 2023 | 2.2 GB |
| `kaggle_nathanlauga_nba_games` | Games, player statistics for each game, daily standings | 2003 to December 2022 | 113 MB |
| `sportsdataverse_injuries` | Official NBA injury reports | December 2018 to November 2026 | 238 MB |
| `boxscorelab` | Season summaries for players and teams, game results, standings | 2022-23 to 2026-27 | 2 MB |

"Play-by-play" means one row for each event in a game, such as a shot, a foul or a substitution.

## Where to find what

| You need | Start with | Other options |
|---|---|---|
| The result of each game | `eoinamoore/Games.csv` | `wyattowalsh/game.csv`, `nathanlauga/games.csv` |
| Team statistics for each game | `eoinamoore/TeamStatistics.csv` | `wyattowalsh/game.csv` (both teams in one row) |
| Player statistics for each game | `eoinamoore/PlayerStatistics.csv` | `nathanlauga/games_details.csv` |
| Advanced statistics for each game | `eoinamoore/TeamStatisticsExtended.csv`, `eoinamoore/PlayerStatisticsExtended.csv` | None |
| Play-by-play | `eoinamoore/PlayByPlay.csv` (includes the x and y position of each shot) | `wyattowalsh/play_by_play.csv` |
| Points in each quarter | `wyattowalsh/line_score.csv` | None |
| Points in the paint, fast-break points, lead changes | `wyattowalsh/other_stats.csv` | None |
| Injuries and absences | `sportsdataverse_injuries/injury_report_*.csv` | `wyattowalsh/inactive_players.csv` |
| Player height, weight and position | `eoinamoore/Players.csv` | `wyattowalsh/common_player_info.csv`, `wyattowalsh/draft_combine_stats.csv` |
| Draft picks | `wyattowalsh/draft_history.csv` | `eoinamoore/Players.csv` |
| Standings during the season | `nathanlauga/ranking.csv` | `boxscorelab/*-team-standings.csv` (end of season only) |
| Upcoming games | `eoinamoore/LeagueSchedule26_27.csv` | None |
| Referees for each game | `wyattowalsh/officials.csv` | `eoinamoore/Games.csv` (`officials` column) |
| Attendance and arena | `eoinamoore/Games.csv` | `wyattowalsh/game_info.csv` |

## How to join files from different sources

Most sources use the official NBA IDs for games, players and teams. You can join their files on these IDs. Each source gives the ID column a different name:

| ID | eoinamoore | wyattowalsh | nathanlauga | sportsdataverse |
|---|---|---|---|---|
| Game | `gameId` | `game_id` | `GAME_ID` | `game_id` |
| Player | `personId` | `person_id`, `player_id`, `player1_id` and similar | `PLAYER_ID` | `person_id` |
| Team | `teamId`, `hometeamId`, `awayteamId` | `team_id`, `team_id_home`, `team_id_away` | `TEAM_ID`, `HOME_TEAM_ID` | `team_id` |

We have not yet checked that the IDs match across sources. Check them before you join files. The boxscorelab files have no IDs, only team names and abbreviations.

---

## kaggle_eoinamoore_historical_nba

Start with this source. It has the most data and runs up to the current season.
It covers the regular season, playoffs, preseason, play-in tournament, NBA Cup and All-Star games. The `gameType` column tells you which.

| File | One row is | Rows | Period |
|---|---|---|---|
| `Games.csv` | a game (result, arena, attendance, referees) | 73,507 | 1946 to 2026 |
| `TeamStatistics.csv` | a team in a game (basic statistics) | 147,016 | 1946 to 2026 |
| `TeamStatisticsExtended.csv` | a team in a game (104 columns, including advanced statistics) | 80,180 | 1996 to 2026 |
| `PlayerStatistics.csv` | a player in a game (basic statistics) | 1,677,321 | 1946 to 2026 |
| `PlayerStatisticsExtended.csv` | a player in a game (110 columns, including advanced statistics) | 844,433 | 1996 to 2026 |
| `PlayByPlay.csv` | an event in a game | 18,864,106 | 1996 to April 2026 |
| `Players.csv` | a player (birth date, height, weight, position, draft) | 6,820 | All years |
| `TeamHistories.csv` | a period in the history of a team (city and name) | 140 | All years |
| `LeagueSchedule24_25.csv`, `LeagueSchedule25_26.csv`, `LeagueSchedule26_27.csv` | a scheduled game | About 1,300 to 1,400 each | One season each |

## kaggle_wyattowalsh_basketball

This source is a historical NBA database, with one table in each file. It ends with the 2023 finals.
We merged its CSV and SQLite copies into one set of files. The [README](../README.md) explains how.

| File | One row is | Rows | Period |
|---|---|---|---|
| `game.csv` | a game, with statistics for both teams | 65,698 | 1946 to 2023 |
| `game_summary.csv` | a game (status, TV broadcaster) | 58,070 | 1946 to 2023 |
| `game_info.csv` | a game (attendance, length) | 58,013 | 1946 to 2023 |
| `line_score.csv` | a game (points in each quarter and overtime) | 58,013 | 1946 to 2023 |
| `other_stats.csv` | a game (points in the paint, second-chance points, leads) | 28,261 | Not stated |
| `play_by_play.csv` | an event in a game | 13,585,539 | 1996 to 2023 |
| `inactive_players.csv` | a player who did not play in a game | 110,184 | Not stated |
| `officials.csv` | a referee in a game | 70,941 | Not stated |
| `common_player_info.csv` | a player (personal and career details) | 4,683 | All years |
| `player.csv` | a player (name, and whether the player is still active) | 4,836 | All years |
| `draft_history.csv` | a draft pick | 8,257 | 1947 to 2023 |
| `draft_combine_stats.csv` | a player at the draft combine, the event where the league measures and tests draft prospects | 1,633 | 2000 to 2023 |
| `team.csv`, `team_details.csv` | a team (city, arena, owner, coach) | 30 | 2023 |
| `team_history.csv` | a period in the history of a team | 60 | All years |
| `team_info_common.csv` | This file is empty. It has column names only. | 0 | None |

## kaggle_nathanlauga_nba_games

This source is smaller and simpler. It covers 2003 to 2022.

| File | One row is | Rows | Period |
|---|---|---|---|
| `games.csv` | a game (points, shooting percentages, whether the home team won) | 26,651 | 2003 to 2022 |
| `games_details.csv` | a player in a game | 668,628 | 2003 to 2022 |
| `ranking.csv` | a team on a given day (wins, losses, winning percentage) | 210,342 | 2003 to 2022 |
| `players.csv` | a player on a team in a season | 7,228 | 2009 to 2019 |
| `teams.csv` | a team | 30 | Not stated |

## sportsdataverse_injuries

These files hold the official NBA injury reports, with one file for each season. The year in the file name is the year the season ends.
The NBA publishes several reports a day, so one player can appear many times for the same game.

| File | One row is | Rows | Period |
|---|---|---|---|
| `injury_report_2019.csv` to `injury_report_2027.csv` | a player in a report (status and reason) | 1,347,766 in total | December 2018 to November 2026 |

The main columns are `game_date`, `team`, `report_player_name`, `current_status` (for example, Out or Questionable), `reason`, `game_id` and `person_id`.

## boxscorelab

These files hold ready-made season summaries, with three files for each season from 2022-23 to 2026-27. The 2026-27 season is still in progress.

| File | One row is | Rows per season |
|---|---|---|
| `<season>-team-game-results.csv` | a team in a game, with estimated offensive and defensive ratings | 2,460 |
| `<season>-player-season-totals.csv` | a player in a season (totals, averages, true shooting percentage, usage rate) | About 460 to 580 |
| `<season>-team-standings.csv` | a team in a season (wins, net rating, pace, strength of schedule) | 30 |

---

## Things to keep in mind

- **Overlap:** The three Kaggle sources cover many of the same games. Start with eoinamoore, which has the most data and the most recent games.
- **Older games:** Games before 1996 have fewer statistics. They have no play-by-play data, and many fields are empty.
- **Current season:** The 2026-27 files include only the games played before we downloaded the data, in mid-November 2026.
- **License:** The wyattowalsh dataset uses the CC BY-SA 4.0 license. If you use it in the report, cite the source.
