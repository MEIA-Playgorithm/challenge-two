import copy
import itertools
import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from plan_substitutions import SubstitutionMDP
from plan_rotation import ROLES


def fixture():
    players=[]
    for i in range(10):
        players.append(dict(player_id=str(i),name=str(i),roles=[ROLES[i%5][0]],available=True,
                            min_minutes=8,max_minutes=36,force_starter=False,
                            predictions={'points':10.,'rebounds_total':float(1 if i<5 else 8),
                                         'assists':float(8 if i<5 else 1)},starter_association=0.))
    config=dict(players=players,block_minutes=4,min_rotation=10,max_rotation=10,
                max_consecutive_blocks=3,weights={'points':1.,'rebounds_total':1.,'assists':1.})
    rows=[]
    for t in range(12):
        group=0 if t%2==0 else 5
        rows.append(dict(block=t,quarter=t//3+1,start_minute=4*t,end_minute=4*t+4,
                         **dict(zip(ROLES,[str(group+i) for i in range(5)]))))
    result=dict(schedule=rows,players=[dict(player_id=str(i),name=str(i),minutes=24,starter=i<5) for i in range(10)])
    return config,result


class SubstitutionTests(unittest.TestCase):
    def test_bellman_and_dominance(self):
        mdp=SubstitutionMDP(*fixture())
        state=mdp.initial()
        action=mdp.choose(state,'mdp')
        prefix,reward,_=mdp.step(state,action)
        expected=reward+sum(mdp.transition[0,c]*mdp.value(prefix+(c,)) for c in range(3))
        self.assertAlmostEqual(mdp.value(state),expected)
        for p in ['fixed','greedy']:
            self.assertGreaterEqual(mdp.value(state)+1e-9,mdp.expected(p))
        np.testing.assert_allclose(mdp.transition.sum(axis=1),1.)

    def test_exhaustive_deterministic_policy_matches_dynamic_program(self):
        mdp=SubstitutionMDP(*fixture(),persistence=1.)
        def enumerate_returns(state):
            if state[0]==mdp.horizon:
                return [0.]
            returns=[]
            for action in mdp.actions(state):
                prefix,reward,_=mdp.step(state,action)
                returns.extend(reward+v for v in enumerate_returns(prefix+(state[-1],)))
            return returns
        self.assertAlmostEqual(max(enumerate_returns(mdp.initial())),mdp.value(mdp.initial()))

    def test_rollouts_preserve_minutes_starters_and_rest(self):
        mdp=SubstitutionMDP(*fixture())
        for contexts in [[0]*12,[0,1,2]*4,[0,2,1]*4]:
            for policy in ['fixed','greedy','mdp']:
                _,_,result=mdp.rollout(contexts,policy)
                self.assertEqual(sum(p['minutes'] for p in result['players']),240)
                self.assertEqual([result['schedule'][0][r] for r in ROLES],['0','1','2','3','4'])

    def test_policy_can_respond_to_context(self):
        mdp=SubstitutionMDP(*fixture(),fatigue=0.,substitution_cost=0.)
        prefix,_,_=mdp.step(mdp.initial(),0)
        actions=[mdp.choose(prefix+(c,),'mdp') for c in [1,2]]
        self.assertNotEqual(set(mdp.lineups[actions[0]]),set(mdp.lineups[actions[1]]))

    def test_invalid_parameters_and_input_are_rejected(self):
        with self.assertRaises(ValueError):
            SubstitutionMDP(*fixture(),persistence=1.1)
        c,r=fixture()
        r['schedule'][0]['C']='0'
        with self.assertRaises(AssertionError):
            SubstitutionMDP(c,r)


if __name__=='__main__':
    unittest.main()
