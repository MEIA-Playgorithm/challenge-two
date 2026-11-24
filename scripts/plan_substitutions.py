"""Finite-horizon MDP for reordering a constrained rotation within quarters."""
from __future__ import annotations
import argparse
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import copy
import numpy as np
import pandas as pd
from plan_rotation import ROLES, verify_solution, plot_rotation

CONTEXTS = ('balanced', 'playmaking', 'rebounding')

class SubstitutionMDP:
    def __init__(self, config, rotation, persistence=.6, fatigue=.08, substitution_cost=.15):
        verify_solution(config, rotation)
        if not 0 <= persistence <= 1 or fatigue < 0 or substitution_cost < 0:
            raise ValueError('Invalid transition or reward parameters')
        self.config, self.rotation = config, rotation
        self.block = config['block_minutes']
        self.horizon = 48//self.block
        self.quarter_blocks = 12//self.block
        if self.quarter_blocks > 3:
            raise ValueError('Exact planner supports blocks of 4, 6 or 12 minutes; finer blocks need another state-space strategy')
        self.players = config['players']
        self.ids = [p['player_id'] for p in self.players]
        self.index = {p:i for i,p in enumerate(self.ids)}
        self.lineups = [tuple(self.index[row[r]] for r in ROLES) for row in rotation['schedule']]
        self.base = np.array([sum(config['weights'][c]*p['predictions'][c] for c in config['weights']) for p in self.players])
        self.context_bonus = np.array([[0]*len(self.ids),
             [.4*p['predictions']['assists'] for p in self.players],
             [.4*p['predictions']['rebounds_total'] for p in self.players]])
        self.transition = np.full((3,3), (1-persistence)/2)
        np.fill_diagonal(self.transition, persistence)
        self.fatigue, self.substitution_cost = fatigue, substitution_cost
        self.decisions = {}
        self.value = lru_cache(None)(self._value)

    def initial(self, context=0):
        return (0, tuple(range(self.quarter_blocks)), (0,)*len(self.ids), -1, context)

    def actions(self, state):
        t, remaining, streak, previous, context = state
        # Equivalent token assignments need only one representative at a decision.
        seen = set()
        for token in remaining:
            if t == 0 and token != 0:
                continue
            lineup = frozenset(self.lineups[token])
            if lineup in seen:
                continue
            seen.add(lineup)
            if any(streak[i] >= self.config['max_consecutive_blocks'] for i in lineup):
                continue
            yield token

    def step(self, state, action):
        t, remaining, streak, previous, context = state
        if action not in remaining:
            raise ValueError('Action must use a remaining block in this quarter')
        lineup = set(self.lineups[action])
        new_streak = tuple(streak[i]+1 if i in lineup else 0 for i in range(len(self.ids)))
        reward = sum((self.base[i]+self.context_bonus[context,i]) *
                     max(0., 1-self.fatigue*streak[i]) for i in lineup)*self.block/48
        incoming = 0 if previous == -1 else len(lineup-set(self.lineups[previous]))
        reward -= self.substitution_cost*incoming
        remaining = tuple(a for a in remaining if a != action)
        if not remaining and t+1 < self.horizon:
            remaining = tuple(range(t+1, t+1+self.quarter_blocks))
        return (t+1, remaining, new_streak, action), float(reward), incoming

    def _value(self, state):
        if state[0] == self.horizon:
            return 0.
        best, chosen = -float('inf'), None
        for action in self.actions(state):
            prefix, reward, _ = self.step(state, action)
            continuation = [self.value(prefix+(c,)) for c in range(3)]
            # Context cannot affect structural feasibility; all continuations must exist.
            if not all(np.isfinite(continuation)):
                continue
            value = reward+float(self.transition[state[-1]] @ continuation)
            if value > best+1e-12:
                best, chosen = value, action
        if chosen is not None:
            self.decisions[state] = chosen
        return best

    def choose(self, state, policy):
        self.value(state)
        if policy == 'mdp':
            return self.decisions[state]
        if policy == 'fixed':
            return state[0]
        if policy == 'greedy':
            choices = []
            for action in self.actions(state):
                prefix, reward, _ = self.step(state, action)
                if np.isfinite(self.value(prefix+(0,))):
                    choices.append((reward, -action, action))
            return max(choices)[2]
        raise ValueError('Unknown policy')

    def expected(self, policy):
        @lru_cache(None)
        def recurse(state):
            if state[0] == self.horizon:
                return 0.
            a = self.choose(state, policy)
            prefix, reward, _ = self.step(state,a)
            return reward+sum(self.transition[state[-1],c]*recurse(prefix+(c,)) for c in range(3))
        return recurse(self.initial())

    def rollout(self, contexts, policy):
        state = self.initial(int(contexts[0]))
        reward_sum, substitutions, rows = 0., 0, []
        for t in range(self.horizon):
            action = self.choose(state, policy)
            prefix,reward,incoming = self.step(state,action)
            row = copy.deepcopy(self.rotation['schedule'][action])
            row.update(block=t, quarter=t//self.quarter_blocks+1,
                       start_minute=t*self.block, end_minute=(t+1)*self.block,
                       source_block=action, context=CONTEXTS[state[-1]], reward=reward,
                       substitutions=incoming)
            rows.append(row)
            reward_sum += reward
            substitutions += incoming
            if t+1 < self.horizon:
                state = prefix+(int(contexts[t+1]),)
        result = copy.deepcopy(self.rotation)
        result['schedule'] = rows
        verify_solution(self.config, result)
        # Preserve the exact per-quarter player budgets, not just full-game totals.
        for q in range(1,5):
            for pid in self.ids:
                before = sum(pid in [r[k] for k in ROLES] for r in self.rotation['schedule'] if r['quarter']==q)
                after = sum(pid in [r[k] for k in ROLES] for r in rows if r['quarter']==q)
                assert before == after
        return reward_sum, substitutions, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rotation-dir', type=Path, default=Path('reports/rotation'))
    parser.add_argument('--output-dir', type=Path, default=Path('reports/substitutions'))
    parser.add_argument('--episodes', type=int, default=500)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--persistence', type=float, default=.6)
    parser.add_argument('--fatigue', type=float, default=.08)
    parser.add_argument('--substitution-cost', type=float, default=.15)
    args = parser.parse_args()
    if args.episodes < 2:
        parser.error('Use at least two episodes')
    if not (args.rotation_dir/'_SUCCESS').exists():
        parser.error('Element 4 must have completed successfully')
    config = json.loads((args.rotation_dir/'inputs.json').read_text())
    rotation = json.loads((args.rotation_dir/'solution.json').read_text())
    mdp = SubstitutionMDP(config, rotation, args.persistence, args.fatigue, args.substitution_cost)
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    (output/'_SUCCESS').unlink(missing_ok=True)
    expected = {p: mdp.expected(p) for p in ['mdp','fixed','greedy']}
    assert expected['mdp']+1e-9 >= max(expected.values())
    rng = np.random.default_rng(args.seed)
    records = []
    example = None
    for episode in range(args.episodes):
        contexts = [0]
        for _ in range(1,mdp.horizon):
            contexts.append(int(rng.choice(3,p=mdp.transition[contexts[-1]])))
        for policy in expected:
            reward,substitutions,result = mdp.rollout(contexts,policy)
            records.append(dict(episode=episode,policy=policy,utility=reward,substitutions=substitutions))
            if episode == 0 and policy == 'mdp':
                example = result
    frame = pd.DataFrame(records)
    frame.to_csv(output/'simulation.csv',index=False)
    wide = frame.pivot(index='episode',columns='policy',values='utility')
    comparisons = {}
    for baseline in ['fixed','greedy']:
        differences = wide.mdp-wide[baseline]
        mean, se = float(differences.mean()),float(differences.std(ddof=1)/np.sqrt(args.episodes))
        comparisons[baseline] = dict(mean_utility_gain=mean, monte_carlo_se=se,
                                     monte_carlo_95_interval=[mean-1.96*se,mean+1.96*se])
    policy_rows = []
    for state,action in sorted(mdp.decisions.items()):
        t,remaining,streak,previous,context = state
        policy_rows.append(dict(block=t,remaining=list(remaining),streak=list(streak),
                                previous=previous,context=CONTEXTS[context],action=action,value=mdp.value(state)))
    (output/'policy.json').write_text(json.dumps({'player_order':mdp.ids, 'player_names':{p['player_id']:p['name'] for p in mdp.players}, 'action_blocks':rotation['schedule'], 'states':policy_rows},indent=2)+'\n')
    pd.DataFrame(example['schedule']).to_csv(output/'example_schedule.csv',index=False)
    plot_rotation(example,output)
    sensitivity = []
    for persistence,fatigue in itertools.product([.3,.8],[0.,.16]):
        alternative = SubstitutionMDP(config,rotation,persistence,fatigue,args.substitution_cost)
        values = {p:alternative.expected(p) for p in ['mdp','fixed']}
        sensitivity.append(dict(persistence=persistence,fatigue=fatigue,**values))
    metrics = dict(expected_utility=expected,comparisons=comparisons,episodes=args.episodes,seed=args.seed,
                   policy_states=len(policy_rows),transition=mdp.transition.tolist(),fatigue=args.fatigue,
                   substitution_cost=args.substitution_cost,sensitivity=sensitivity,
                   scope='Synthetic context transitions and utility; no real-game win claim',
                   source_sha256={n:hashlib.sha256((args.rotation_dir/n).read_bytes()).hexdigest()
                                  for n in ['inputs.json','solution.json']})
    (output/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    lines=['# Substitution policy results','',
           'The finite-horizon Markov decision process reorders quarter blocks while preserving the Element 4 minute budgets.',
           'Contexts, fatigue effects and substitution costs are simulation assumptions, not estimated causal basketball effects.','',
           '| Policy | Exact expected utility |','| --- | ---: |']
    lines += [f'| {p} | {v:.4f} |' for p,v in expected.items()]
    lines += ['',f'Evaluated {args.episodes} paired simulated context paths. Exported {len(policy_rows)} decision states.',
              'All exported and simulated rotations passed the Element 4 checks and exact per-quarter minute checks.',
              'The optimality statement applies only to this finite action set, transition model and utility.', '',
              '![Example substitution schedule](rotation.png)', '',
              'The chart shows the first seeded simulation, not an expected or observed real-game rotation.', '',
              'See [the method guide](../../docs/SUBSTITUTION_PLANNING.md) for the state, Bellman equation and limitations.']
    lines += ['', 'A [genetic algorithm comparison](../genetic_substitutions/RESULTS.md) evaluates the same decision problem.']
    (output/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    (output/'_SUCCESS').write_text('Finite MDP solved and simulated rotations verified.\n')
    print(json.dumps(metrics,indent=2))

if __name__ == '__main__':
    main()
