# Predict game results

Element 2 predicts the probability that the home team wins before a game starts.
It uses the game and team tables from [data preparation](DATA_PREPARATION.md).
Read the [experiment results](../reports/result_prediction/RESULTS.md) for measured performance and figures.

## Reproduce the experiment

Use Python 3.11 or later. Install the recorded ML dependencies in a virtual environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-ml.lock
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/train_results.py --output reports/result_prediction_run2
```

On Windows, use `.venv/Scripts/python` in place of `.venv/bin/python`.
The lock file records the versions used for the included experiment.
The default input is `data/processed/`. It must contain a completed preparation run.
The output directory must be new, so each experiment keeps its own results.

The default preparation scope gives these splits:

| Split | Seasons | Games in the recorded run |
| --- | --- | ---: |
| Train | 2019–20 to 2023–24 | 5,829 |
| Validation | 2024–25 | 1,224 |
| Test | 2025–26 | 1,230 |

Regular-season IDs include Cup games that count toward the regular season.
The source has missing or unusable games in 2024–25. Histories reflect the available records.

## Build features without future results

The script creates one row per game and 46 model features.
It processes games by date. It creates every forecast for a day before applying that day's results.
This also prevents an earlier game on the same day from entering another game's features.

For each team, it calculates means over the last 5 games, last 10 games and current season.
Each model feature represents the home team's mean minus the away team's mean.
The 13 measurements are wins, points for and against, point margin, assists, rebounds,
turnovers, field-goal percentage, three-point percentage, free-throw percentage,
effective field-goal percentage, offensive rating and defensive rating.

Offensive and defensive ratings use an approximate possession count:

```text
estimated team possessions = field-goal attempts + 0.44 × free-throw attempts
                             − offensive rebounds + turnovers
game possessions = mean of both teams' estimated possessions
offensive rating = 100 × team points / game possessions
defensive rating = 100 × opponent points / game possessions
```

These estimates are not the provider's official advanced ratings.
All statistics enter the history only after that prediction day has finished.

Seven additional features describe games played this season, days since the last game,
back-to-back games and the difference between team Elo ratings.
Days since the last game are capped at 14. Missing history stays missing until preprocessing.
Rolling statistics reset each season. Elo retains 75% of its distance from 1,500 between seasons.
Elo starts at 1,500, uses K=20 and adds 65 points for home advantage.
These parameters are fixed before evaluation.

The training pipeline fits median imputation, missing-value indicators and, for logistic regression,
standardization using training data only. It never uses the target, current box score, IDs,
dates or split labels as model features.
The feature table retains those fields only for auditing and evaluation.

## Compare and select models

The script evaluates six learned candidates:

- Logistic regression with C values of 0.1, 1 and 10.
- Random Forest with 300 trees, depth 10 and a minimum of 15 samples per leaf.
- Histogram gradient boosting with depth 3, 200 iterations and L2 values of 1 and 10.

The fixed references are the historical home-win frequency and the Elo probability.
The home-frequency reference predicts home wins when that frequency exceeds 0.5.

The script selects the learned candidate with the lowest validation log loss.
It then refits that candidate on training plus validation data.
The held-out test evaluates this frozen model and both references.
During testing, histories may use completed games from earlier test days.
This evaluates daily forecasts rather than a forecast for an entire season made on opening day.

Accuracy measures correct classifications at a 0.5 threshold.
Log loss and Brier score measure probability error; lower values are better.
ROC-AUC measures discrimination; higher values are better.
Calibration and ROC plots complement these scores.

Permutation importance uses validation data before the final refit.
It measures the increase in log loss after shuffling a feature.
Correlated features can share importance, and a negative value can reflect noise.

## Use the saved model

The prediction command builds the same features from games before the requested date.
Provide NBA team IDs, the date and the season start year:

```bash
.venv/bin/python scripts/predict_game.py \
  --date 2026-10-20 --season-start 2026 \
  --home-team-id 1610612738 --away-team-id 1610612747
```

This command illustrates a hypothetical Boston–Los Angeles fixture; it does not consult a schedule.
The output includes both win probabilities, the model's training cutoff and the age of the available history.
The script rejects dates within the model's training period and unknown or identical team IDs.
Update the prepared history before using predictions for a later season.
Use `--model` to select a model from another experiment.

## Files produced

| File | Contents |
| --- | --- |
| `game_features.csv` | Features, targets, split labels and history cutoff dates |
| `feature_dictionary.csv` | Definitions of all 46 model inputs |
| `model.joblib` | Fitted preprocessing and estimator, feature list and training cutoff |
| `metrics.json` | Validation and test metrics, settings, package versions and input fingerprints |
| `input_quality_report.json` | The preparation manifest used by this experiment |
| `test_predictions.csv` | Every held-out game, its result and predicted probabilities |
| `validation_feature_importance.csv` | Validation permutation importance and variation across repeats |
| `test_calibration_roc.png` | Test calibration and discrimination plots |
| `validation_feature_importance.png` | The 12 highest validation importance values |
| `RESULTS.md` | Experiment report |
| `_SUCCESS` | Confirmation that training and saved-model verification finished |

The generated model and full feature table remain local. The smaller reports and predictions can be versioned.
Tests verify that changing current or future results cannot change current features.
They also cover same-day exclusion, season resets and forecasts without a known result.
Training checks that the saved model reproduces the probabilities used for evaluation.

## Interpret the result

The recorded experiment selected logistic regression with C=0.1.
It reached 67.2% test accuracy, compared with 55.4% for the home-frequency reference.
Elo reached 67.8% accuracy. Logistic regression had slightly lower log loss: 0.603 versus 0.608.
These point estimates do not prove a significant difference between the two approaches.

The model excludes injuries because report timezones have not been verified.
It does not model expected lineups, player transfers or neutral venues explicitly.
Source gaps, the 2019–20 bubble and later source corrections also limit the experiment.
Use the model as an evaluated academic baseline, with the limitations recorded alongside its metrics.
