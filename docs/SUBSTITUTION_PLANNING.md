# Plan substitutions with a Markov decision process

Element 5 adapts the order of substitutions within each quarter of the Element 4 rotation.
It solves a finite-horizon Markov decision process (MDP) by backward dynamic programming.
The player priorities come from Element 3 through the saved Element 4 inputs.

Run the planner after generating the Element 4 rotation:

```bash
.venv/bin/python scripts/plan_substitutions.py
.venv/bin/python scripts/query_substitution.py
```

Read the [experiment report](../reports/substitutions/RESULTS.md) for measured results.
The default experiment uses the same retrospective Boston scenario as Element 4.
It assumes the roster and availability in that scenario remain valid throughout the game.

## State and actions

A state contains:

- The current time-block index, from 0 to 12 in the four-minute example.
- The remaining original block identifiers in the current quarter.
- Each player's consecutive blocks on court, ordered by `player_order` in the policy file.
- The identifier of the preceding lineup block, or −1 before tip-off.
- One observed context: `balanced`, `playmaking` or `rebounding`.

These variables determine legal actions, rewards and transition probabilities.
The remaining blocks encode the quarter's outstanding minute allocations.
Earlier quarters always consume their original budgets, so full historical minute counters are unnecessary here.

An action selects one remaining block's five-player role assignment to play next.
The planner preserves the original starting five by requiring original block 0 first.
It removes the chosen block from the current quarter's remaining set.
At the next quarter, it loads that quarter's original blocks.
Equivalent five-player sets need only one representative action at a state.

The action set is deliberately restricted. It reorders existing lineups instead of creating new ones.
It preserves every player's exact minutes in each quarter and therefore throughout the game.
The original positions, availability, rotation size and minute bounds remain satisfied.
The planner rejects actions that exceed the consecutive-block limit.
Backward recursion also excludes actions that leave no feasible completion.
Quarter breaks do not reset consecutive-block counters, matching Element 4.

The exact implementation supports four-, six- and twelve-minute blocks.
It rejects finer blocks to avoid silently entering an impractically large permutation search.
The default makes a decision every four game minutes, including a decision to keep the same lineup.

## Transition model

Court occupancy and consecutive-block counters change deterministically after the selected action.
The context for the next block follows this default transition matrix:

| Current / next | Balanced | Playmaking | Rebounding |
| --- | ---: | ---: | ---: |
| Balanced | 0.6 | 0.2 | 0.2 |
| Playmaking | 0.2 | 0.6 | 0.2 |
| Rebounding | 0.2 | 0.2 | 0.6 |

Every episode starts in `balanced` context.
The context is an abstract tactical demand, not an opponent classification learned from tracking data.
The matrix is an explicit simulation assumption. It is independent of the selected action.
Use `--persistence` to change the diagonal probability; the remaining probability is shared equally.
Real deployment would require a reliable context observation rule and calibrated transitions.

## Reward and solution

The production priority `U[i]` is the weighted predicted production defined in Element 4.
The context bonus is zero in balanced mode, 0.4 times predicted assists in playmaking mode,
and 0.4 times predicted rebounds in rebounding mode.

For one block, the reward is:

```text
sum over active players:
    (U[i] + context_bonus[i]) * max(0, 1 - fatigue * previous_streak[i]) * block_minutes / 48
minus substitution_cost * number_of_entering_players
```

Defaults are `fatigue = 0.08` and `substitution_cost = 0.15`.
The starting five incurs no substitution cost.
Fatigue resets after one block off court; this is a simplified assumption, not a physiological model.
The starter-association term is omitted because the starting five is fixed and that term would be constant.

We maximize undiscounted total utility over the finite game horizon:

```text
V(terminal_state) = 0
V(state) = max over feasible actions:
    reward(state, action) + sum P(next_context | context) * V(next_state)
```

The implementation memoizes state values and exports the maximizing action for every evaluated feasible decision state.
Optimality applies to this restricted action set and assumed reward and transitions.
It does not establish that these substitutions improve real scores or win probabilities.
The model excludes score differential, foul trouble, new injuries, overtime and opponent lineup changes.
Those factors require additional state variables and validated transition estimates.

## Evaluation and interpretation

We compare three policies:

- `mdp`: maximizes expected total remaining reward.
- `fixed`: follows the original Element 4 block order.
- `greedy`: maximizes immediate reward among actions with a feasible completion.

The greedy policy uses the feasibility recursion but does not use future utility to rank its actions.
We calculate exact expected utility from the same transition matrix for all three policies.
We also simulate 500 context paths, using identical paths for all policies in each comparison.
Seed 42 makes the simulation reproducible.

The default Boston experiment finds equal expected utility for all three policies.
Its simulated gain is zero. The report does not claim an improvement where none was measured.
The constrained quarter budgets and rest limits restrict how much the policy can adapt.
Sensitivity runs vary persistence between 0.3 and 0.8 and fatigue between 0 and 0.16.
They solve each alternative model again and compare it with the original fixed ordering.
These runs describe dependence on assumptions; they do not validate those assumptions.

The confidence intervals in `metrics.json` measure Monte Carlo uncertainty in paired simulated utility differences.
They do not include ML prediction error, parameter uncertainty or real-game outcome uncertainty.
All simulated schedules receive independent position, availability, minute, starter and rest checks.
Additional checks ensure exact per-quarter player-minute preservation.
Tests compare dynamic programming against exhaustive enumeration in a small deterministic example.

## Query an observed state

The default query prints the initial five. To query later, create a JSON file containing:

```json
{
  "block": 1,
  "remaining": [1, 2],
  "streak": [1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
  "previous": 0,
  "context": "playmaking"
}
```

The streak array above is only a format example. Build its values from the actual preceding lineup,
in the exact `player_order` of your policy. Do not assume that ordering matches jersey numbers or the roster display.
`remaining` lists unconsumed original block IDs in ascending order; `previous` is an original block ID, not elapsed time.

```bash
.venv/bin/python scripts/query_substitution.py --state /path/to/state.json
```

The command returns the chosen role assignments, entering players, leaving players and remaining expected utility.
A missing state produces an error rather than silently recommending an unrelated action.
If availability, minute allocations or the roster change, regenerate Element 4 and then this policy.
Context must be observed at decision time; do not supply future contexts when making a decision.

## Files and parameters

Outputs are written to `reports/substitutions/` by default:

| File | Contents |
| --- | --- |
| `policy.json` | State-action table, player order, names and original block assignments |
| `metrics.json` | Exact expectations, paired comparisons, sensitivity results, parameters and source hashes |
| `simulation.csv` | Utility and replacement counts for every episode and policy |
| `example_schedule.csv` | First seeded MDP trajectory, including contexts and substitutions |
| `rotation.png` | Chart of that example trajectory |
| `RESULTS.md` | Readable experiment summary |
| `_SUCCESS` | Successful solution and simulation checks |

Change the assumptions or run more simulations with:

```bash
.venv/bin/python scripts/plan_substitutions.py \
  --persistence 0.8 --fatigue 0.04 --substitution-cost 0.1 \
  --episodes 1000 --seed 42 --output-dir reports/substitutions_custom
```

Use `--rotation-dir` to load another completed Element 4 scenario.
Run verification with `.venv/bin/python -m unittest discover -s tests`.

## Compare with a genetic algorithm

Element 5 also supports evolving an adaptive substitution policy with a genetic algorithm.
The comparison uses identical transitions, utility and feasible actions, with five independent genetic runs.
Read the [genetic comparison guide](GENETIC_SUBSTITUTIONS.md) and [results](../reports/genetic_substitutions/RESULTS.md).
Run `.venv/bin/python scripts/compare_genetic_substitutions.py` to reproduce the experiment.
