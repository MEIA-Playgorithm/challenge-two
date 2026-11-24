import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from test_substitutions import fixture
from compare_genetic_substitutions import GeneticMDP,feasible_policy_space,evolve,policy_value


class GeneticTests(unittest.TestCase):
    def test_evolution_is_reproducible_feasible_and_elitist(self):
        mdp=GeneticMDP(*fixture(),fatigue=0.,substitution_cost=0.)
        with patch.object(mdp,'value',side_effect=AssertionError('Genetic search must not consult Bellman values')):
            states,options=feasible_policy_space(mdp)
            actions,run,history=evolve(mdp,states,options,42,12,8,.2)
            again,run2,_=evolve(mdp,states,options,42,12,8,.2)
        self.assertEqual(actions,again)
        self.assertEqual(run['fitness'],run2['fitness'])
        self.assertTrue(all(b['best']>=a['best']-1e-12 for a,b in zip(history,history[1:])))
        self.assertTrue(all(a in options[s] for s,a in actions.items()))
        self.assertLessEqual(run['fitness'],mdp.value(mdp.initial())+1e-8)
        mdp.genetic_actions=actions
        for contexts in [[0]*12,[0,1,2]*4]:
            _,_,result=mdp.rollout(contexts,'ga')
            self.assertEqual(sum(p['minutes'] for p in result['players']),240)

    def test_fixed_policy_fitness_matches_existing_evaluation(self):
        mdp=GeneticMDP(*fixture())
        states,options=feasible_policy_space(mdp)
        # Off-path states are irrelevant; the fixed path always retains its next original block.
        actions={s:(s[0] if s[0] in options[s] else options[s][0]) for s in states}
        fitness,_=policy_value(mdp,actions)
        self.assertAlmostEqual(fitness,mdp.expected('fixed'))

    def test_invalid_genetic_parameters(self):
        mdp=GeneticMDP(*fixture())
        states,options=feasible_policy_space(mdp)
        with self.assertRaises(ValueError):evolve(mdp,states,options,42,population=2)
        with self.assertRaises(ValueError):evolve(mdp,states,options,42,mutation=2)

if __name__=='__main__':unittest.main()
