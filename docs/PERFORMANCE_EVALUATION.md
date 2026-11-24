# Evaluate players and starting lineups

Element 3 evaluates player production and starting-lineup associations with game outcomes.
Run the experiment after preparing the shared datasets:

```bash
.venv/bin/python scripts/train_performance.py
.venv/bin/python -m unittest discover -s tests
```

The default inputs are `data/processed/games.csv` and `player_games.csv`.
Use `--data-dir` and `--output-dir` to change paths.
The [experiment report](../reports/performance/RESULTS.md) contains measured results.
The environment versions are recorded in `requirements-ml.lock`.

## Evaluate player production

We predict points, total rebounds and assists for each appearance.
These separate targets avoid imposing arbitrary weights on a single player score.
Each row requires recorded participation and five earlier appearances in the same season.
This is a conditional production model. It does not predict injuries, selection or availability.

Features contain home status, rest days and the number of available historical appearances, capped at ten.
They also contain five-game and ten-game means of seven statistics:
points, rebounds, assists, steals, blocks, turnovers and field-goal attempts.
Histories reset each season and follow players across team changes within that season.
Every game on a calendar day receives features before that day's outcomes update histories.
Minutes are excluded because source minute encodings need further validation.
Career summaries and current-game box-score values are excluded from predictors.

We compare Ridge regression, Random Forest and the last-ten-appearance mean.
The selection criterion is validation mean absolute error, averaged across the three targets.
This equal weighting uses raw statistic units; points may dominate the criterion.
Imputation and scaling are fitted inside each training pipeline.
The selected estimator is refitted on training plus validation data.
If the historical mean wins, we retain that reference instead of forcing a learned estimator.
Test history updates use earlier observed test games, while model parameters stay fixed.

The test summary records observed production and actual points minus predicted points.
A positive residual means production exceeded the model's expectation.
It does not establish player quality or causal contribution to winning.
Use the eligibility flag to limit comparisons to players with at least 20 evaluated appearances.
Early-season and short-career appearances are absent, which affects representativeness.

## Evaluate starting lineups

We require exactly five distinct starters per team, with no player shared by both teams.
We exclude games with incomplete or invalid starter records and export their identifiers.
The basic and extended player sources share the large starter gap in 2021–22.
The coverage file shows exclusions by season.

Each game has one row. Its target is home points minus away points.
The sparse feature matrix assigns +1 to each home starter and −1 to each away starter.
A second candidate adds an indicator for each complete five-player combination.
Ridge regression reduces unstable coefficients for rare players and combinations.
We select the feature set and regularization on validation root mean squared error.
The home-mean baseline is also eligible for selection.
Unknown test players and combinations receive zero learned contribution.
The metrics include the number of unknown test player slots.

The intercept captures the fitted home advantage.
The lineup summary sums its player and combination coefficients, excluding the intercept.
These values are associations with full-game margin, expressed in points.
Coefficients depend on regularization and the observed opponents and teammates.
They are not causal player ratings, possession-based net ratings or adjusted on-court plus-minus.
Bench performance and coaching remain unmeasured confounders.

The summary also records the observed full-game margin when each quintet started.
Use its eligibility flag to restrict comparisons to quintets with at least ten test starts.
Observed starters are retrospective inputs. Their availability before tip-off is not verified.
This experiment does not reconstruct substitutions or evaluate all in-game combinations.
That extension requires validated court occupancy and score attribution at substitution boundaries.
Do not use these results to claim which substitution or lineup would cause a better outcome.

## Read the outputs

All files are written to `reports/performance/`:

| File | Contents |
| --- | --- |
| `RESULTS.md` | Measured results and scope |
| `metrics.json` | Validation candidates, test errors, counts and input SHA-256 hashes |
| `player_test_predictions.csv` | Actual, predicted and baseline values for each player appearance |
| `player_test_summary.csv` | Player production and residual summaries |
| `lineup_test_predictions.csv` | Actual and predicted full-game margins |
| `starting_lineup_test_summary.csv` | Starting-quintet associations and observed margins |
| `lineup_coefficients.csv` | Fitted player and quintet coefficients |
| `lineup_coverage.csv` | Accepted and excluded games by season |
| `excluded_lineup_games.csv` | Games rejected by starter checks |
| `player_model.joblib`, `lineup_model.joblib` | Fitted estimators and feature metadata |
| `_SUCCESS` | Successful completion of this experiment |

Training uses seasons starting in 2019 through 2023.
Validation uses 2024–25. The held-out test uses 2025–26.
We report mean absolute error, root mean squared error and R-squared.
The fixed split supports reproducibility but does not measure uncertainty across alternative seasons.
Model files use Python serialization; load only files from a trusted source.

## Score supplied starting quintets

After training, supply five player IDs for each side:

```bash
.venv/bin/python scripts/evaluate_lineup.py \
  --home 2544 203076 1626156 1630559 1629029 \
  --away 201939 203110 203952 1627780 1630228
```

This syntax example does not assert that those players form a current roster.
The command reports the expected full-game home margin and unknown player IDs.
It does not validate roster membership or predict a win probability.
The saved model includes data through 2024–25; use it only for later games when evaluating prospectively.
