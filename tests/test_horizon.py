import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.plan_horizon import win_distribution,select_candidates,validate_fixtures,forecasts
from scripts.train_results import VERSION


class FakeModel:
    def predict_proba(self,x):
        return np.array([[.25,.75]])


def candidate(day,minutes,utility):
    return dict(game_date=day,weighted_utility=utility,rotation={'players':[
        dict(player_id='a',minutes=minutes),dict(player_id='b',minutes=48-minutes)]})


class HorizonTests(unittest.TestCase):
    def test_win_distribution_matches_enumeration(self):
        np.testing.assert_allclose(win_distribution([.5,.5]),[.25,.5,.25])
        np.testing.assert_allclose(win_distribution([1,0]),[0,1,0])
        with self.assertRaises(ValueError): win_distribution([1.1])

    def test_global_budget_changes_individual_best_choices(self):
        options=[[candidate('2026-01-01',36,10),candidate('2026-01-01',24,8)],
                 [candidate('2026-01-03',36,20),candidate('2026-01-03',24,5)]]
        result=select_candidates(options,60,64)
        self.assertEqual(result['selected'],[1,0])
        self.assertEqual(result['total_minutes']['a'],60)

    def test_back_to_back_and_infeasibility(self):
        options=[[candidate('2026-01-01',36,10)], [candidate('2026-01-02',36,20)]]
        self.assertEqual(select_candidates(options,96,64)['status'],'INFEASIBLE')
        self.assertEqual(select_candidates([[]],96,64)['status'],'INFEASIBLE')

    def test_invalid_schedule(self):
        f=dict(game_date='2026-01-01',home_team_id='a',away_team_id='b')
        with self.assertRaises(ValueError):validate_fixtures([f,f],'a','2026-01-01')
        with self.assertRaises(ValueError):validate_fixtures([f],'c','2026-01-01')

    def test_every_forecast_uses_one_shared_information_cutoff(self):
        games=pd.DataFrame([dict(game_id=str(i),game_datetime_source=f'2026-01-0{i} 12:00:00',
                                 home_team_id='a',away_team_id='b') for i in [1,2,3]])
        teams=pd.DataFrame({'game_id':['1','2','3'],'team_score':[100,200,300]})
        fixtures=[dict(game_date=f'2026-01-0{i}',home_team_id='a',away_team_id='b',season_start=2025) for i in [2,3]]
        calls=[]
        def build(g,t,fixture):
            calls.append((g.game_id.tolist(),t.game_id.tolist()))
            return pd.DataFrame([dict(game_id='fixture',feature=1)])
        artifact=dict(feature_version=VERSION,trained_through='2025-01-01',model=FakeModel(),features=['feature'])
        with patch('plan_horizon.build_features',side_effect=build):
            predictions=forecasts(games,teams,fixtures,'2026-01-02','a',artifact)
        self.assertEqual(calls,[(['1'],['1']),(['1'],['1'])])
        self.assertEqual([p['win_probability'] for p in predictions],[.75,.75])

if __name__=='__main__':unittest.main()
