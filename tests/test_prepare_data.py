import argparse
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location('prepare_data', Path(__file__).parents[1] / 'scripts/prepare_data.py')
prep = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prep)


class PreparationTests(unittest.TestCase):
    def test_identifiers_and_minutes(self):
        self.assertEqual(prep.identifier('0021900001', True), '0021900001')
        self.assertEqual(prep.identifier('21900001.0', True), '0021900001')
        self.assertEqual(prep.identifier('1628427.0'), '1628427')
        self.assertEqual(float(prep.minutes('12:30')), 12.5)
        self.assertEqual(prep.minutes(''), '')
        self.assertEqual(prep.minutes('0'), '0')
        with self.assertRaises(ValueError):
            prep.identifier('2.19e7', True)
        with self.assertRaises(ValueError):
            prep.minutes('12:99')
        with self.assertRaises(ValueError):
            prep.minutes('-1:30')

    def test_pipeline_preserves_time_and_quarantines_bad_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'csv'
            out = Path(tmp) / 'processed'

            def write(path, fields, rows):
                path = root / path
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('w', newline='') as stream:
                    writer = csv.DictWriter(stream, fields)
                    writer.writeheader()
                    writer.writerows(rows)

            games = [dict(gameId=f'2{year}00001', gameDateTimeEst=f'20{year}-12-25 19:00:00',
                          hometeamId='1', awayteamId='2', homeScore='100', awayScore='90',
                          hometeamCity='Home', hometeamName='Team', awayteamCity='Away', awayteamName='Team',
                          winner='1', gameType='Regular Season') for year in (19, 20, 21)]
            games[1]['gameType'] = 'NBA Emirates Cup'
            write(f'{prep.PRIMARY}/Games.csv', list(games[0]), games)
            teams, players = [], []
            for game in games:
                for team in ('1', '2'):
                    teams.append(dict(gameId=game['gameId'], teamId=team,
                                      opponentTeamId='2' if team == '1' else '1',
                                      teamScore='100' if team == '1' else '90', numMinutes='240'))
                    players.append(dict(gameId=game['gameId'], playerteamId=team,
                                        opponentteamId='2' if team == '1' else '1',
                                        playerteamCity='Home' if team == '1' else 'Away', playerteamName='Team',
                                        opponentteamCity='Away' if team == '1' else 'Home', opponentteamName='Team',
                                        home='1' if team == '1' else '0',
                                        personId=team, numMinutes='12:30'))
            players[0]['playerteamId'] = ''
            players[0]['opponentteamId'] = ''
            invalid = dict(teams[0], teamId='9')
            for name in ('TeamStatistics.csv', 'TeamStatisticsExtended.csv'):
                write(f'{prep.PRIMARY}/{name}', list(teams[0]), teams + [teams[0], invalid])
            for name in ('PlayerStatistics.csv', 'PlayerStatisticsExtended.csv'):
                write(f'{prep.PRIMARY}/{name}', list(players[0]), players)
            write(f'{prep.PRIMARY}/Players.csv',
                  ['personId', 'firstName', 'lastName', 'heightInches', 'bodyWeightLbs'],
                  [dict(personId='1', firstName='One', lastName='Player', heightInches='80', bodyWeightLbs='200')])
            write('kaggle_wyattowalsh_basketball/game.csv',
                  ['game_id', 'game_date', 'team_id_home', 'team_id_away', 'pts_home', 'pts_away'],
                  [dict(game_id='0021900001', game_date='2019-12-25', team_id_home='1', team_id_away='2',
                        pts_home='100', pts_away='90')])
            write('kaggle_nathanlauga_nba_games/games.csv',
                  ['GAME_ID', 'GAME_DATE_EST', 'HOME_TEAM_ID', 'VISITOR_TEAM_ID', 'PTS_home', 'PTS_away'], [])
            write('kaggle_wyattowalsh_basketball/common_player_info.csv',
                  ['person_id', 'display_first_last'], [{'person_id': '1', 'display_first_last': 'One Player'}])
            injury = dict(game_id='0021900001', team_id='1', person_id='1', game_date='2019-12-25',
                          report_datetime='2019-12-25T17:00:00', current_status='Questionable')
            write('sportsdataverse_injuries/injury_report_2020.csv', list(injury),
                  [injury, injury, dict(injury, report_datetime='2019-12-25T18:00:00', current_status='Out')])
            event = dict.fromkeys(prep.EVENT_COLUMNS, '')
            event.update(gameId='21900001', teamId='1', personId='1', clock='PT12M00.00S',
                         period='1', actionNumber='1', actionType='period')
            # Distinct events sharing an action number must survive.
            event2 = dict(event, actionType='substitution', subsInPersonId='2')
            write(f'{prep.PRIMARY}/PlayByPlay.csv', prep.EVENT_COLUMNS, [event, event, event2])
            args = argparse.Namespace(input=root, output=out, start_season=2019, end_season=2021)
            prep.Pipeline(args).run()
            report = json.loads((out / 'quality_report.json').read_text())
            self.assertEqual(report['tables']['games']['rows'], 3)
            self.assertEqual(report['tables']['team_games']['rows'], 6)
            self.assertEqual(report['tables']['player_games']['rows'], 6)
            self.assertEqual(report['tables']['repairs']['rows'], 4)
            self.assertEqual(report['tables']['injury_reports']['rows'], 2)
            self.assertEqual(report['tables']['play_by_play']['rows'], 2)
            self.assertEqual(report['checks']['players_missing_biography'], ['2'])
            self.assertEqual(report['checks']['quarantine_reasons']['duplicate business key'], 2)
            self.assertEqual(report['checks']['quarantine_reasons']['team not in game'], 2)
            self.assertEqual(report['checks']['play_by_play']['games_without_events'], 2)
            self.assertEqual(report['checks']['event_identity']['ambiguous_keys'], 1)
            self.assertEqual(report['checks']['event_identity']['records_with_ambiguous_key'], 2)
            with (out / 'games.csv').open() as stream:
                prepared = list(csv.DictReader(stream))
            self.assertEqual([r['split'] for r in prepared], ['train', 'validation', 'test'])
            self.assertEqual(prepared[0]['game_id'], '0021900001')
            self.assertTrue((out / '_SUCCESS').exists())
            with self.assertRaises(FileExistsError):
                prep.Pipeline(args)


if __name__ == '__main__':
    unittest.main()
