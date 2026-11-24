import copy
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from plan_rotation import solve, validate_config, verify_solution


def fixture():
    roles = ['G']*4+['F']*4+['C']*2
    return dict(block_minutes=4, min_rotation=8, max_rotation=10, max_consecutive_blocks=3,
                weights={'points': 1., 'rebounds_total': 1.2, 'assists': 1.5}, starter_weight=1.,
                players=[dict(player_id=str(i), name=f'Player {i}', roles=[role], available=True,
                              min_minutes=8, max_minutes=36, force_starter=False,
                              predictions={'points': float(i+1), 'rebounds_total': 3., 'assists': 2.},
                              starter_association=float(i)) for i,role in enumerate(roles)])


class RotationTests(unittest.TestCase):
    def test_feasible_and_exported_constraints(self):
        config = fixture()
        config['players'][0]['force_starter'] = True
        result = solve(config, 5)
        self.assertIn(result['status'], ['FEASIBLE', 'OPTIMAL'])
        verify_solution(config, result)
        self.assertEqual(sum(p['minutes'] for p in result['players']), 240)
        self.assertTrue(result['players'][0]['starter'])
        broken = copy.deepcopy(result)
        broken['schedule'][0]['C'] = broken['schedule'][0]['G1']
        with self.assertRaises(AssertionError):
            verify_solution(config, broken)

    def test_unavailable_player_receives_no_minutes(self):
        config = fixture()
        config['players'][0]['available'] = False
        result = solve(config, 5)
        self.assertIn(result['status'], ['FEASIBLE', 'OPTIMAL'])
        self.assertEqual(result['players'][0]['minutes'], 0)

    def test_missing_center_capacity_is_infeasible(self):
        config = fixture()
        config['players'][9]['available'] = False
        result = solve(config, 5)
        self.assertEqual(result['status'], 'INFEASIBLE')
        self.assertNotIn('schedule', result)

    def test_forced_unavailable_starter_is_infeasible(self):
        config = fixture()
        config['players'][0].update(available=False, force_starter=True)
        self.assertEqual(solve(config, 5)['status'], 'INFEASIBLE')

    def test_reject_nonrepresentable_minutes(self):
        config = fixture()
        config['players'][0]['max_minutes'] = 35
        with self.assertRaises(ValueError):
            validate_config(config)

    def test_multirole_player_cannot_fill_two_slots(self):
        config = fixture()
        for p in config['players']:
            p['roles'] = ['G','F','C']
        result = solve(config, 5)
        self.assertIn(result['status'], ['FEASIBLE','OPTIMAL'])
        verify_solution(config, result)


if __name__ == '__main__':
    unittest.main()
