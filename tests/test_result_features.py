import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))

import numpy as np
import pandas as pd

from train_results import FEATURES, build_features


class TemporalFeatureTests(unittest.TestCase):
    def setUp(self):
        self.games = pd.DataFrame([
            dict(game_id='001', game_datetime_source='2020-01-01 18:00:00', season_start=2019,
                 home_team_id='A', away_team_id='B', home_win=1, split='train'),
            dict(game_id='002', game_datetime_source='2020-01-02 18:00:00', season_start=2019,
                 home_team_id='B', away_team_id='A', home_win=0, split='train'),
            dict(game_id='003', game_datetime_source='2020-01-02 23:00:00', season_start=2019,
                 home_team_id='A', away_team_id='B', home_win=1, split='train'),
            dict(game_id='004', game_datetime_source='2020-01-03 18:00:00', season_start=2019,
                 home_team_id='A', away_team_id='B', home_win=0, split='train'),
        ])
        rows = []
        for game in self.games.to_dict('records'):
            for team in ('A', 'B'):
                rows.append(dict(game_id=game['game_id'], team_id=team, team_score=110 if team == 'A' else 100,
                                 field_goals_attempted=80, field_goals_made=40, three_pointers_made=10,
                                 free_throws_attempted=20, rebounds_offensive=10, turnovers=12, assists=25,
                                 rebounds_total=45, field_goals_percentage=0.5,
                                 three_pointers_percentage=0.4, free_throws_percentage=0.8))
        self.teams = pd.DataFrame(rows)

    def test_current_and_future_results_do_not_change_current_features(self):
        original = build_features(self.games, self.teams)
        changed_games, changed_teams = self.games.copy(), self.teams.copy()
        changed_games.loc[changed_games['game_id'] >= '002', 'home_win'] = 1
        changed_teams.loc[changed_teams['game_id'] >= '002', 'team_score'] = 300
        modified = build_features(changed_games, changed_teams)
        before = original.loc[original['game_id'] <= '003', FEATURES]
        after = modified.loc[modified['game_id'] <= '003', FEATURES]
        pd.testing.assert_frame_equal(before, after)
        self.assertFalse(np.allclose(original.loc[3, FEATURES].to_numpy(dtype=float),
                                     modified.loc[3, FEATURES].to_numpy(dtype=float), equal_nan=True))

    def test_same_day_games_are_excluded_and_missing_history_is_explicit(self):
        frame = build_features(self.games, self.teams)
        self.assertTrue(pd.isna(frame.loc[0, 'diff_last5_margin']))
        self.assertEqual(frame.loc[1, 'home_games_played'], 1)
        self.assertEqual(frame.loc[2, 'home_games_played'], 1)
        self.assertEqual(frame.loc[3, 'home_games_played'], 3)
        self.assertTrue((frame['latest_history_date'].dropna() < frame.loc[frame['latest_history_date'].notna(), 'game_date']).all())
        self.assertNotIn('home_win', FEATURES)
        self.assertNotIn('game_id', FEATURES)

    def test_new_season_resets_statistics_and_forecast_needs_no_target(self):
        fixture = {'game_date': '2020-12-25', 'season_start': 2020, 'home_team_id': 'A', 'away_team_id': 'B'}
        row = build_features(self.games, self.teams, fixture=fixture).iloc[-1]
        self.assertEqual(row['game_id'], 'fixture')
        self.assertTrue(pd.isna(row['home_win']))
        self.assertEqual(row['home_games_played'], 0)
        self.assertTrue(pd.isna(row['diff_season_win']))
        self.assertEqual(row['home_rest_days'], 14)
        self.assertNotEqual(row['elo_difference'], 0)

    def test_forecast_excludes_later_games_in_input(self):
        fixture = {'game_date': '2020-01-02', 'season_start': 2019, 'home_team_id': 'A', 'away_team_id': 'B'}
        full = build_features(self.games, self.teams, fixture=fixture).iloc[-1]
        prefix = build_features(self.games.iloc[:1], self.teams, fixture=fixture).iloc[-1]
        pd.testing.assert_series_equal(full[FEATURES], prefix[FEATURES])


if __name__ == '__main__':
    unittest.main()
