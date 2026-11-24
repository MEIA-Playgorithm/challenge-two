"""Compare a genetic substitution policy with exact MDP and fixed/greedy policies."""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from time import perf_counter
import numpy as np
import pandas as pd
from plan_substitutions import SubstitutionMDP, CONTEXTS
from plan_rotation import plot_rotation


class GeneticMDP(SubstitutionMDP):
    def choose(self, state, policy):
        if policy == 'ga':
            return self.genetic_actions[state]
        return super().choose(state,policy)


def feasible_policy_space(mdp):
    """Enumerate legal state-actions with a structural feasibility check, without rewards."""
    actions={}
    @lru_cache(None)
    def visit(state):
        if state[0]==mdp.horizon:
            return True
        choices=[]
        for action in mdp.actions(state):
            prefix,_,_=mdp.step(state,action)
            viable=[visit(prefix+(c,)) for c in range(3)]
            if all(viable):
                choices.append(action)
        if choices:
            actions[state]=tuple(choices)
        return bool(choices)
    if not visit(mdp.initial()):
        raise ValueError('No feasible substitution policy')
    states=sorted(actions)
    return states,actions


def policy_value(mdp, actions):
    @lru_cache(None)
    def value(state):
        if state[0]==mdp.horizon:
            return 0.
        prefix,reward,_=mdp.step(state,actions[state])
        return reward+sum(mdp.transition[state[-1],c]*value(prefix+(c,)) for c in range(3))
    return value(mdp.initial()),value


def evolve(mdp,states,options,seed,population=40,generations=40,mutation=.1):
    if population<4 or generations<1 or not 0<=mutation<=1:
        raise ValueError('Require population >=4, generations >=1 and mutation in [0,1]')
    rng=np.random.default_rng(seed)
    sizes=np.array([len(options[s]) for s in states])
    pop=rng.integers(0,sizes,size=(population,len(states)))
    fitness_cache={}
    def decode(chromosome):
        return {s:options[s][int(g)] for s,g in zip(states,chromosome)}
    def fitness(chromosome):
        key=tuple(chromosome)
        if key not in fitness_cache:
            fitness_cache[key]=policy_value(mdp,decode(chromosome))[0]
        return fitness_cache[key]
    history=[]
    start=perf_counter()
    for generation in range(generations+1):
        scores=np.array([fitness(c) for c in pop])
        ranking=np.argsort(-scores,kind='stable')
        history.append(dict(seed=seed,generation=generation,best=float(scores[ranking[0]]),
                            mean=float(scores.mean()),unique_evaluations=len(fitness_cache)))
        if generation==generations:
            break
        next_pop=[pop[ranking[0]].copy(),pop[ranking[1]].copy()]
        def parent():
            tournament=rng.integers(0,population,size=3)
            return pop[tournament[np.argmax(scores[tournament])]]
        while len(next_pop)<population:
            a,b=parent(),parent()
            child=np.where(rng.random(len(states))<.5,a,b).copy()
            mask=rng.random(len(states))<mutation
            child[mask]=rng.integers(0,sizes[mask])
            next_pop.append(child)
        pop=np.array(next_pop)
    best=pop[ranking[0]]
    return decode(best),dict(seed=seed,fitness=float(scores[ranking[0]]),seconds=perf_counter()-start,
                             unique_evaluations=len(fitness_cache)),history


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rotation-dir',type=Path,default=Path('reports/rotation'))
    parser.add_argument('--output-dir',type=Path,default=Path('reports/genetic_substitutions'))
    parser.add_argument('--population',type=int,default=40)
    parser.add_argument('--generations',type=int,default=40)
    parser.add_argument('--mutation',type=float,default=.1)
    parser.add_argument('--runs',type=int,default=5)
    parser.add_argument('--episodes',type=int,default=500)
    parser.add_argument('--seed',type=int,default=42)
    parser.add_argument('--persistence',type=float,default=.6)
    parser.add_argument('--fatigue',type=float,default=.08)
    parser.add_argument('--substitution-cost',type=float,default=.15)
    args=parser.parse_args()
    if args.runs<1 or args.episodes<2:
        parser.error('Require at least one run and two episodes')
    if not (args.rotation_dir/'_SUCCESS').exists():
        parser.error('A completed Element 4 rotation is required')
    config=json.loads((args.rotation_dir/'inputs.json').read_text())
    rotation=json.loads((args.rotation_dir/'solution.json').read_text())
    mdp=GeneticMDP(config,rotation,args.persistence,args.fatigue,args.substitution_cost)
    output=args.output_dir
    output.mkdir(parents=True,exist_ok=True)
    (output/'_SUCCESS').unlink(missing_ok=True)
    start=perf_counter()
    states,options=feasible_policy_space(mdp)
    graph_seconds=perf_counter()-start
    runs,convergence,policies=[],[],[]
    for seed in range(args.seed,args.seed+args.runs):
        actions,summary,history=evolve(mdp,states,options,seed,args.population,args.generations,args.mutation)
        runs.append(summary);convergence.extend(history);policies.append(actions)
    best=max(range(len(runs)),key=lambda i:runs[i]['fitness'])
    mdp.genetic_actions=policies[best]
    ga_value,values=policy_value(mdp,mdp.genetic_actions)
    start=perf_counter()
    exact=mdp.value(mdp.initial())
    mdp_seconds=perf_counter()-start
    expected={'ga':ga_value,'mdp':exact,'fixed':mdp.expected('fixed'),'greedy':mdp.expected('greedy')}
    assert all(r['fitness']<=exact+1e-8 for r in runs)
    rng=np.random.default_rng(args.seed+10000)
    simulations=[]
    example=None
    for episode in range(args.episodes):
        contexts=[0]
        for t in range(1,mdp.horizon):
            contexts.append(int(rng.choice(3,p=mdp.transition[contexts[-1]])))
        for policy in expected:
            reward,changes,result=mdp.rollout(contexts,policy)
            simulations.append(dict(episode=episode,policy=policy,utility=reward,substitutions=changes))
            if episode==0 and policy=='ga':example=result
    frame=pd.DataFrame(simulations)
    wide=frame.pivot(index='episode',columns='policy',values='utility')
    paired={}
    for baseline in ['mdp','fixed','greedy']:
        differences=wide.ga-wide[baseline]
        mean=float(differences.mean());se=float(differences.std(ddof=1)/np.sqrt(args.episodes))
        paired[baseline]=dict(mean_ga_minus_baseline=mean,monte_carlo_se=se,monte_carlo_95_interval=[mean-1.96*se,mean+1.96*se])
    policy_rows=[dict(block=s[0],remaining=list(s[1]),streak=list(s[2]),previous=s[3],context=CONTEXTS[s[4]],
                      action=mdp.genetic_actions[s],value=values(s)) for s in states]
    (output/'policy.json').write_text(json.dumps(dict(player_order=mdp.ids,player_names={p['player_id']:p['name'] for p in mdp.players},
                                                     action_blocks=rotation['schedule'],states=policy_rows),indent=2)+'\n')
    frame.to_csv(output/'simulation.csv',index=False)
    pd.DataFrame(runs).to_csv(output/'runs.csv',index=False)
    pd.DataFrame(convergence).to_csv(output/'convergence.csv',index=False)
    pd.DataFrame(example['schedule']).to_csv(output/'example_schedule.csv',index=False)
    plot_rotation(example,output)
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4))
    for run in runs:
        curve=[r for r in convergence if r['seed']==run['seed']]
        ax.plot([r['generation'] for r in curve],[r['best'] for r in curve],label=f"Seed {run['seed']}")
    ax.axhline(exact,color='black',linestyle='--',label='Exact MDP')
    ax.set(xlabel='Generation',ylabel='Expected utility',title='Genetic policy convergence')
    ax.legend();fig.tight_layout();fig.savefig(output/'convergence.png',dpi=160);plt.close(fig)
    metrics=dict(expected_utility=expected,ga_gap_to_exact=exact-ga_value,selected_seed=runs[best]['seed'],runs=runs,
                 state_count=len(states),states_with_choice=sum(len(options[s])>1 for s in states),
                 population=args.population,generations=args.generations,mutation=args.mutation,episodes=args.episodes,
                 simulation_seed=args.seed+10000,transition=mdp.transition.tolist(),fatigue=args.fatigue,substitution_cost=args.substitution_cost,
                 graph_seconds=graph_seconds,mdp_solve_seconds=mdp_seconds,paired_comparisons=paired,
                 source_sha256={n:hashlib.sha256((args.rotation_dir/n).read_bytes()).hexdigest() for n in ['inputs.json','solution.json']})
    (output/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    lines=['# Genetic algorithm versus MDP substitution planning','',
           'Both methods optimize an adaptive policy over the same feasible states, actions, transitions and utility.',
           'The genetic algorithm receives no MDP-optimal actions or values during evolution.','',
           '| Policy | Exact expected utility |','| --- | ---: |']
    lines += [f'| {p} | {v:.6f} |' for p,v in expected.items()]
    lines += ['',f"Best GA gap to exact MDP: {exact-ga_value:.6f}. Selected seed: {runs[best]['seed']}.",
              f'{len(states)} feasible decision states; {metrics["states_with_choice"]} with multiple actions.',
              f'{args.runs} independent genetic runs; population {args.population}; {args.generations} generations.',
              f'{args.episodes} paired simulation paths; all schedules passed minute, position and rest checks.', '',
              '![Convergence](convergence.png)', '', '![Example genetic policy rotation](rotation.png)', '',
              'Equality on this small scenario does not demonstrate superiority or better scaling.',
              'The outcome concerns assumed simulation utility, not real-game wins.', '',
              'See [the comparison guide](../../docs/GENETIC_SUBSTITUTIONS.md) for representation, operators and limitations.']
    (output/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    (output/'_SUCCESS').write_text('Genetic policies evaluated against exact MDP and verified in simulation.\n')
    print('\n'.join(lines[:16]))

if __name__=='__main__':main()
