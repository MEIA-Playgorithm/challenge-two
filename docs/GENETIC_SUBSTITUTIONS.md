# Compare genetic and Markov substitution policies

Element 5 now includes a genetic algorithm (GA) as an alternative optimizer for substitution policies.
Both optimizers use the same Markov state, transitions, rewards and legal actions.
The GA searches for an adaptive policy, not a fixed schedule compared unfairly with an adaptive MDP.

```bash
.venv/bin/python scripts/compare_genetic_substitutions.py
```

Read the [comparison report](../reports/genetic_substitutions/RESULTS.md).
The command uses the completed Element 4 plan in `reports/rotation/`.
It computes the MDP reference again with identical parameters and leaves the original reports unchanged.
The [MDP guide](SUBSTITUTION_PLANNING.md) defines the shared state, actions and simulation assumptions.

## Genetic representation and operators

A chromosome has one integer gene for each feasible decision state.
Its value indexes the legal actions for that state.
Actions select remaining quarter blocks; they preserve the original starters and quarter-level minute budgets.
A structural recursion removes choices that cannot finish within the rest constraints.
This feasibility calculation does not inspect rewards or Bellman-optimal values.
The implementation tests that evolution never calls the MDP optimizer.

Initial chromosomes contain randomly selected legal genes.
Each generation uses tournaments of three individuals to choose parents.
Uniform crossover independently selects each gene from either parent with probability 0.5.
Mutation resamples each gene from its legal range with default probability 0.1.
Resampling can retain the original value. Two elite individuals survive unchanged.
These operators cannot introduce an illegal action at a state.

The default population is 40, with 40 generations after initial evaluation.
Five independent seeds, 42 through 46, measure variation between runs.
Fitness is exact expected total utility under the assumed transition matrix.
A memoized policy evaluation sums rewards and transition-weighted continuation values.
It evaluates a fixed chromosome; it does not maximize actions as the Bellman optimizer does.
Repeated chromosomes reuse their cached fitness.
The best run is selected by exact expected utility, before simulated comparisons.

## Fair comparison and its limits

We report exact expected utility for the selected GA policy, exact MDP, fixed rotation and greedy policy.
The MDP value supplies an upper bound on achievable expected utility in this finite model.
Each GA run must remain below or equal to that bound within numerical tolerance.

The four policies also use the same 500 simulated context paths.
Simulation uses seed 10042, separate from evolution seeds.
Every resulting schedule passes independent constraints and per-quarter minute checks.
Paired confidence intervals describe simulation sampling error only, not real basketball uncertainty.

The base scenario gives all four policies expected utility 131.774382.
All five genetic runs reach the MDP value.
However, only three of the 46 feasible decision states offer multiple actions.
The eight possible chromosomes are all evaluated in these runs.
This is a small, restrictive comparison; it does not establish superior search efficiency or scaling for GA.
The convergence plot can therefore be flat from generation zero.

The [zero-fatigue sensitivity report](../reports/genetic_substitutions_no_fatigue/RESULTS.md)
shows the same comparison when the assumed fatigue penalty is removed.
It is a sensitivity analysis, not evidence that basketball players experience no fatigue.

Structural state enumeration, exact fitness and a full state-action chromosome limit scalability.
The implementation inherits the MDP planner's four-, six- and twelve-minute block restriction.
A larger action space would need a compact policy representation or approximate fitness evaluation.
GA is stochastic and does not generally prove optimality; matching the exact bound proves it only for that run and model.

Run timings are recorded separately for feasibility enumeration, each genetic run and the MDP solve.
GA timings include population evolution and fitness caching; graph setup is reported separately.
They exclude simulations, plotting and export. They are not a controlled runtime benchmark.

## Outputs and queries

Outputs are saved to `reports/genetic_substitutions/`:

| File | Contents |
| --- | --- |
| `RESULTS.md` | Comparison and limitations |
| `metrics.json` | Parameters, exact values, gaps, timings, paired differences and source hashes |
| `runs.csv` | Best fitness, duration and unique evaluations for each seed |
| `convergence.csv` | Best and mean fitness by generation |
| `convergence.png` | Fitness curves and exact MDP reference |
| `policy.json` | Selected adaptive GA policy |
| `simulation.csv` | Per-episode utility and replacement counts for all four methods |
| `example_schedule.csv` | First seeded GA trajectory |
| `rotation.png` | That trajectory's court schedule |
| `_SUCCESS` | Completed and checked comparison |

The policy uses the same query format as the MDP policy:

```bash
.venv/bin/python scripts/query_substitution.py \
  --policy reports/genetic_substitutions/policy.json
```

Add `--state state.json` for a later observed state, following the MDP guide.
The `value` field is the selected policy's expected continuation value, not a claim of globally optimal value.

## Change the experiment

```bash
.venv/bin/python scripts/compare_genetic_substitutions.py \
  --population 60 --generations 80 --mutation 0.15 --runs 10 \
  --episodes 1000 --seed 42 --output-dir reports/genetic_custom
```

Shared model parameters are `--persistence`, `--fatigue` and `--substitution-cost`.
For the supplied sensitivity report, run:

```bash
.venv/bin/python scripts/compare_genetic_substitutions.py \
  --fatigue 0 --output-dir reports/genetic_substitutions_no_fatigue
```

Use `--rotation-dir reports/horizon/game_01` to compare policies for an Element 6 game.
This does not modify that game's selected minute allocation or replace its integrated MDP policy automatically.

Run `.venv/bin/python -m unittest discover -s tests`.
Tests cover reproducibility, elitism, legal genes, independence from MDP-optimal values,
fitness evaluation, simulated constraint preservation and the exact upper bound.
