# Genetic algorithm versus MDP substitution planning

Both methods optimize an adaptive policy over the same feasible states, actions, transitions and utility.
The genetic algorithm receives no MDP-optimal actions or values during evolution.

| Policy | Exact expected utility |
| --- | ---: |
| ga | 131.774382 |
| mdp | 131.774382 |
| fixed | 131.774382 |
| greedy | 131.774382 |

Best GA gap to exact MDP: 0.000000. Selected seed: 42.
46 feasible decision states; 3 with multiple actions.
5 independent genetic runs; population 40; 40 generations.
500 paired simulation paths; all schedules passed minute, position and rest checks.

![Convergence](convergence.png)

![Example genetic policy rotation](rotation.png)

Equality on this small scenario does not demonstrate superiority or better scaling.
The outcome concerns assumed simulation utility, not real-game wins.

See [the comparison guide](../../docs/GENETIC_SUBSTITUTIONS.md) for representation, operators and limitations.
