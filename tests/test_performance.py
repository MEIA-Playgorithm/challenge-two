import importlib.util
from pathlib import Path
import unittest

import pandas as pd

spec = importlib.util.spec_from_file_location('performance', Path(__file__).resolve().parents[1]/'scripts/train_performance.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PerformanceTests(unittest.TestCase):
    def test_current_and_future_outcomes_cannot_change_features(self):
        records = []
        for i in range(8):
            records.append(dict(game_id=str(i), player_id='a', team_id='t', game_date=f'2025-01-{i+1:02}',
                                season_start=2024, participation_status='played', first_name='A', last_name='B',
                                home=1, **{c: float(i+1) for c in m.HISTORY}))
        p = pd.DataFrame(records)
        games = pd.DataFrame({'game_id': [str(i) for i in range(8)], 'split': ['validation']*8})
        original = m.player_features(p, games)
        p.loc[5:, m.HISTORY] = 999
        altered = m.player_features(p, games)
        cols = [c for c in original if '_last' in c]
        pd.testing.assert_series_equal(original.iloc[0][cols], altered.iloc[0][cols])
        self.assertEqual(original.iloc[0].points_last5, 3)

    def test_same_day_outcomes_are_not_used(self):
        rows = [dict(game_id=str(i), player_id='a', team_id='t', game_date=f'2025-01-{min(i+1,6):02}',
                     season_start=2024, participation_status='played', first_name='A', last_name='B',
                     home=1, **{c: i+1 for c in m.HISTORY}) for i in range(7)]
        games = pd.DataFrame({'game_id': [str(i) for i in range(7)], 'split': ['test']*7})
        f = m.player_features(pd.DataFrame(rows), games)
        self.assertEqual(f.points_last5.tolist(), [3., 3.])

    def test_lineup_swap_changes_sign_and_order_does_not_matter(self):
        a, b = ('1','2','3','4','5'), ('6','7','8','9','10')
        x = m.lineup_features(a,b)
        self.assertEqual(x, m.lineup_features(tuple(reversed(a)), b))
        self.assertEqual(x, {k: -v for k,v in m.lineup_features(b,a).items()})

    def test_reject_incomplete_starters(self):
        p = pd.DataFrame(
            [dict(game_id='g', team_id=t, player_id=str(i), starting_position='G')
             for t, ids in [('h', range(5)), ('a', range(5,9))] for i in ids])
        g = pd.DataFrame([dict(game_id='g', game_date='2025-01-01', season_start=2024, split='validation',
                              home_team_id='h', away_team_id='a', home_score=100, away_score=99)])
        accepted, rejected = m.starting_lineups(p,g)
        self.assertTrue(accepted.empty)
        self.assertEqual(len(rejected), 1)


if __name__ == '__main__':
    unittest.main()
