# Plan goals and player use across games

Element 6 connects the prepared data, result forecasts, player models, rotation constraints and substitution policies.
It produces a multi-game plan with a win goal and shared player-minute limits.

```bash
.venv/bin/python scripts/plan_horizon.py
```

The default example plans Boston's next three recorded fixtures from April 1, 2026.
The goal is at least two wins. Each player has a 96-minute horizon limit.
Consecutive-day fixtures have a combined 64-minute limit per player.
Read the [generated report](../reports/horizon/RESULTS.md) for probabilities and selected plans.

## Integration contracts

| Element | Input to this planner | Use |
| --- | --- | --- |
| 1: Preparation | Completed `data/processed/` tables | Historical observations and fixture calendar |
| 2: Result prediction | `reports/result_prediction/model.joblib` | Per-game win probabilities |
| 3: Performance | Saved production and starter models | Frozen player priorities and starter associations |
| 4: Constraints | `build_roster`, `solve`, `verify_solution` | Candidate rotations and independent checks |
| 5: MDP | `SubstitutionMDP` | Adaptive block ordering for every selected rotation |
| 6: Horizon | Win target and shared minute budgets | Joint candidate selection and goal assessment |

The orchestrator reuses these modules directly. It does not retrain the models.
Run preparation and model training before running this command.
Completed standalone Element 4 and 5 reports are not required: their functions run inside this planner.

## Forecasts and goals

All result observations are frozen strictly before the planning cutoff, including for later horizon games.
The cutoff must follow the saved models' final training dates.
The code checks result feature compatibility and the performance model's input hashes.
The player roster and predictions are also built once at the cutoff.

The fixture calendar supplies dates and team identities, never future scores or box scores.
Rest features account for scheduled games before each fixture, including other teams' recorded calendar entries.
This retrospective example assumes those calendar entries were known at the cutoff.
The source does not provide a historically versioned schedule, so postponed or rescheduled games can affect this assumption.
Team statistics, games-played counts and Elo remain frozen. No fictitious results update them.
Forecasts farther into the horizon therefore represent a frozen-strength approximation.

Player priorities remain fixed in the home context for all games, including away games.
This provides a consistent allocation score; it is not a fresh per-game production prediction.
The plan assumes a stable roster within one season. Per-game unavailability can be supplied explicitly.
It excludes new injuries, transfers and changes in role unless you regenerate the plan.

Expected wins are the sum of the per-game win probabilities.
The win-count distribution is the convolution of individual Bernoulli outcome distributions.
The probability of meeting the goal is the probability of at least `target_wins` victories.
This distribution assumes independent outcomes. Correlated injuries, team form and model errors are not represented.
Expected wins do not require independence, but the reported goal probability does.
A target is an uncertain sporting objective, not a guaranteed constraint or promised result.

## Allocate minutes across games

For each game, Element 4 generates candidates with individual minute caps of 36, 32 and 28.
All other roster, role, rotation-size and consecutive-block constraints remain active.
Unavailable players receive zero minutes. Infeasible candidates are excluded and candidate counts are reported.
Each candidate supplies exactly 240 player-minutes with an explicit court schedule.

A second CP-SAT model chooses exactly one candidate per game.
For each player, the sum of minutes across the horizon cannot exceed `max_total_minutes`.
For each pair of listed consecutive-day games, their combined minutes cannot exceed `back_to_back_cap`.
The final selection receives independent checks of both limits.

The objective sums each candidate's rotation utility multiplied by `1 + 4*p*(1-p)`.
Here `p` is the forecast win probability. This heuristic gives greater priority to more evenly matched games.
It is a planning preference, not an estimated return on effort or a learned effect on wins.
The win target is reported separately; the solver does not pretend that rotation utility changes win probability.

`OPTIMAL` means optimal among the generated candidates, using rounded integer objective coefficients.
It does not mean globally optimal over all possible joint rotations.
A candidate can be merely `FEASIBLE` if its individual solve reaches the ten-second limit.
Candidate statuses are recorded in `metrics.json`.
The final candidate-selection solve has a 30-second limit and records its bound.
An infeasible candidate set exits with code 2 and produces no success marker.
Another feasible rotation may exist outside that candidate set.

The MDP then computes an exact finite-horizon policy for each selected rotation.
Because it preserves quarter-level minute totals, its decisions also preserve the cross-game budgets.
Its reward and transition assumptions are those documented in the [substitution guide](SUBSTITUTION_PLANNING.md).
Its reward is distinct from the rotation objective and is reported separately.
The exported schedule example uses balanced context throughout; the policy supports all modeled contexts.

## Configure the horizon

```bash
.venv/bin/python scripts/plan_horizon.py \
  --team-id 1610612738 --cutoff 2026-04-01 --games 3 \
  --target-wins 2 --max-total-minutes 96 --back-to-back-cap 64 \
  --output-dir reports/horizon_custom
```

Use `--fixtures schedule.json` for a custom chronological JSON array:

```json
[
  {
    "game_id": "scenario_1",
    "game_date": "2026-04-01",
    "home_team_id": "1610612738",
    "away_team_id": "1610612748",
    "season_start": 2025,
    "unavailable": ["1628369"]
  }
]
```

This is a format example, not a claim about an actual fixture or injury.
With one supplied game, also set `--target-wins 1`.
Every fixture must involve the selected team. Dates must be distinct, ordered and at or after the cutoff.
Include every team game in the horizon: minute budgets cover only listed games.
Changing `--games` does not truncate an explicitly supplied fixture array.

The candidate roster inherits Element 4's limitations: recent team records, biography positions and assumed availability.
Excluded candidates and source/model hashes are retained in each game's `inputs.json`.
The model does not infer medical availability or prescribe safe workload limits.
Minute caps are user-adjustable planning assumptions.

## Read the results

| File | Contents |
| --- | --- |
| `RESULTS.md` | Win goal, probabilities and links to game plans |
| `games.csv` | Forecasts, chosen caps and per-game utility summaries |
| `player_totals.csv` | Cumulative minutes for every candidate player |
| `win_distribution.csv` | Probability of each possible win count |
| `selection.json` | Solver status, chosen candidates, objective, bound and minute totals |
| `metrics.json` | Parameters, assumptions, candidates and provenance |
| `game_XX/inputs.json` | Per-game roster and constraints |
| `game_XX/solution.json` | Original constrained rotation |
| `game_XX/policy.json` | MDP policy compatible with the substitution query command |
| `game_XX/substitutions.csv` | Balanced-context example schedule |
| `game_XX/minutes.csv` | Player minute allocation |
| `game_XX/rotation.png` | Example court schedule |
| `_SUCCESS` | Complete integrated run |

Query a game's policy with:

```bash
.venv/bin/python scripts/query_substitution.py --policy reports/horizon/game_01/policy.json
```

Use a fresh output directory for distinct scenarios. The root success marker is removed before a new run.
An interrupted or failed run can leave older per-game files; only use the directory when its root success marker exists.

## Replan and verify

After a game, update the prepared observations, model artifacts when appropriate and availability.
Then move the cutoff forward and generate the remaining horizon again.
Updated prepared files require rebuilding the performance artifacts because their input hashes are enforced.
This explicit rerun is the receding-horizon workflow; the script does not monitor live games automatically.
No simulation result is treated as an observed box score.

Run `.venv/bin/python -m unittest discover -s tests`.
Tests cover the win distribution, shared information cutoff, cross-game budget tradeoffs,
consecutive-day infeasibility and invalid schedules, alongside the earlier modules' checks.
