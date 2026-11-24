# Plan the starting five and minutes

Element 4 uses constraint programming to select starters and generate a complete regulation-game rotation.
It uses the saved player-production and starter-association models from Element 3.

## Run the example

Install the project requirements, prepare the data and train Element 3 first.
Then run:

```bash
.venv/bin/python scripts/plan_rotation.py
```

The default scenario uses Boston (`1610612738`) on April 1, 2026, as the home team.
This is a retrospective planning example, not a verified fixture or current roster recommendation.
The [generated report](../reports/rotation/RESULTS.md) shows starters, minutes and solver status.

Choose another scenario with:

```bash
.venv/bin/python scripts/plan_rotation.py \
  --team-id 1610612738 --date 2026-04-01 \
  --output-dir reports/rotation_custom
```

Add `--away` to build player-production features for an away game.
The opponent is not modeled by this planner.
For the additive starter model, a fixed opponent contribution would be constant across candidate lineups.

## How ML supplies the objective

We rebuild each candidate's features using appearances strictly before the scenario's calendar date.
We use the Element 3 feature builder and saved production estimator.
The same-season history requirement remains five earlier appearances.
No actual target-game production or starter list enters these features.
The saved models include 2024–25, so the planner rejects dates at or before their training cutoff.
Input hashes must match the data recorded by the ML experiment.

The default production priority is:

`U[i] = predicted_points + 1.2 * predicted_rebounds + 1.5 * predicted_assists`

We clip negative statistical predictions to zero.
The optimization objective is:

`sum(U[i] * planned_minutes[i] / 48) + starter_weight * sum(starter_association[i] * starts[i])`

`starter_association` is the additive player coefficient from the selected starting-lineup Ridge model.
The default starter weight is 1.0. Unknown players receive a zero starter coefficient and are flagged in the inputs.
The constant home intercept does not affect selection and is omitted.
This planner rejects models with quintet interaction terms rather than silently dropping those terms.

These weights express planning preferences. They were not learned or validated as coaching decisions.
The player estimator predicts production per appearance, not marginal production per minute.
Therefore, minute-weighted utility is a heuristic priority score, not a prediction of points or wins.
The objective does not establish that changing minutes causes better performance.
It can favor high-volume players whose historical production reflects larger roles.
The saved model's predictive errors remain relevant uncertainty; this is not a robust optimization model.

## Constraints and decision variables

We use the OR-Tools CP-SAT solver.
Boolean variables record whether each player occupies each role in each time block.
Other Boolean variables record court participation and rotation membership.
The first block defines the starting five.

The default model enforces:

- Twelve four-minute blocks covering 48 regulation minutes.
- Exactly five distinct players in every block.
- Two guard slots, two forward slots and one center slot in every block.
- At most one role per player per block, including players eligible for several roles.
- Exactly 240 total player-minutes, implied by complete court coverage.
- Eight to ten players used in the rotation.
- Eight to 36 minutes for each selected player; unused players receive zero minutes.
- At most three consecutive blocks per player, followed by at least one block off court.
- Zero minutes for unavailable players.
- Every player marked `force_starter` in the starting five.

The positional template is a configurable roster eligibility assumption, not a mandatory NBA lineup rule.
The G/F/C roles do not distinguish point guards from shooting guards or small forwards from power forwards.
Quarter boundaries do not reset the rest constraint; this is a conservative modeling choice.
The model excludes overtime, foul trouble, injuries during play and opponent substitutions.
It allows substitutions at every block boundary without a limit on simultaneous replacements.

## Edit the roster and limits

The script writes all predictions, coefficients, roles and limits to `inputs.json`.
Copy that file, edit it and solve again:

```bash
cp reports/rotation/inputs.json configs/rotation_custom.json
.venv/bin/python scripts/plan_rotation.py \
  --config configs/rotation_custom.json --output-dir reports/rotation_custom
```

Set `available` to `false` to exclude a player.
Change `min_minutes`, `max_minutes` or `force_starter` to express coaching constraints.
Minimum minutes apply only if a player is selected.
Set `min_rotation` and `max_rotation` to control rotation size.
Set `weights` and `starter_weight` to change planning priorities.

`block_minutes` must be a positive integer divisor of 12.
Player minute limits must be exact multiples of that block length.
For example, two-minute blocks support a 34-minute cap and offer a finer schedule.
`max_consecutive_blocks` counts blocks, so adjust it when changing block length.

The generated candidate roster uses each player's latest earlier team record within 30 days.
This can miss recent signings or include unavailable players.
Availability is assumed; injury reports are not interpreted as verified pregame availability.
Position eligibility comes from the player biography snapshot, which is not historically versioned.
Review roles and roster membership before operational use.
Candidates with fewer than five earlier season appearances or no position are listed as excluded.
The example does not invent predictions for those candidates.

The `--config` path uses the stored predictions exactly as supplied.
Changing its date does not refresh predictions. Generate new inputs for a new scenario date.

## Outputs and verification

| File | Contents |
| --- | --- |
| `inputs.json` | Editable roster, ML scores, constraints and source/model hashes |
| `solution.json` | Solver status, utility, upper bound and full solution |
| `schedule.csv` | Role assignment in every time block, using player IDs |
| `minutes.csv` | Names, minutes, starters and objective components |
| `RESULTS.md` | Readable summary |
| `rotation.png` | Chart of court participation and assigned roles |
| `_SUCCESS` | A feasible plan was exported and independently checked |

`OPTIMAL` proves optimality for the integer objective and supplied constraints.
`FEASIBLE` means a valid plan was found but optimality was not proved within the time limit.
Scores are scaled by 1,000 and rounded for CP-SAT, so reported utility has rounding error.
`best_bound` is an upper bound on that rounded objective.
Use `--time-limit 60` to allow a longer solve. One worker and seed 42 support reproducibility.

`INFEASIBLE` means the supplied constraints cannot all hold.
`UNKNOWN` can mean the time limit expired before finding a solution.
Neither status produces a successful schedule. The command exits with code 2.
Previous successful artifacts in that output directory are cleared before a new solve.

After solving, independent checks validate the exported schedule's positions, availability, starters, minutes and rest.
Run the test suite with:

```bash
.venv/bin/python -m unittest discover -s tests
```
