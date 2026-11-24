#!/usr/bin/env python3
"""Train and evaluate pregame NBA home-win probability models."""

import argparse
import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/challenge-two-matplotlib')

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits


SEED = 42
VERSION = 'pregame-daily-v1'
METRICS = ['win', 'points_for', 'points_against', 'margin', 'assists', 'rebounds',
           'turnovers', 'fg_percentage', 'three_percentage', 'ft_percentage',
           'effective_fg_percentage', 'offensive_rating', 'defensive_rating']
CONTEXT = ['home_games_played', 'away_games_played', 'home_rest_days', 'away_rest_days',
           'home_back_to_back', 'away_back_to_back', 'elo_difference']
FEATURES = [f'diff_{window}_{metric}' for window in ('last5', 'last10', 'season')
            for metric in METRICS] + CONTEXT
IDS = {key: 'string' for key in ['game_id', 'team_id', 'home_team_id', 'away_team_id']}


def load_history(directory):
    directory = Path(directory)
    if not (directory / '_SUCCESS').exists():
        raise ValueError('Use a completed preparation run with an _SUCCESS marker.')
    games = pd.read_csv(directory / 'games.csv', dtype=IDS, low_memory=False)
    teams = pd.read_csv(directory / 'team_games.csv', dtype=IDS, low_memory=False)
    if games['game_id'].duplicated().any() or teams.duplicated(['game_id', 'team_id']).any():
        raise ValueError('Input keys are not unique.')
    return games, teams


def safe_ratio(a, b):
    return a / b if pd.notna(a) and pd.notna(b) and b > 0 else np.nan


def team_observation(team, opponent, won):
    own_possessions = (team['field_goals_attempted'] + 0.44 * team['free_throws_attempted']
                       - team['rebounds_offensive'] + team['turnovers'])
    opponent_possessions = (opponent['field_goals_attempted'] + 0.44 * opponent['free_throws_attempted']
                            - opponent['rebounds_offensive'] + opponent['turnovers'])
    possessions = (own_possessions + opponent_possessions) / 2
    return dict(win=float(won), points_for=team['team_score'], points_against=opponent['team_score'],
                margin=team['team_score'] - opponent['team_score'], assists=team['assists'],
                rebounds=team['rebounds_total'], turnovers=team['turnovers'],
                fg_percentage=team['field_goals_percentage'], three_percentage=team['three_pointers_percentage'],
                ft_percentage=team['free_throws_percentage'],
                effective_fg_percentage=safe_ratio(team['field_goals_made'] + 0.5 * team['three_pointers_made'],
                                                  team['field_goals_attempted']),
                offensive_rating=100 * safe_ratio(team['team_score'], possessions),
                defensive_rating=100 * safe_ratio(opponent['team_score'], possessions))


def summarize(history):
    result = {}
    for window, observations in [('last5', history[-5:]), ('last10', history[-10:]), ('season', history)]:
        for metric in METRICS:
            values = [r[metric] for r in observations if pd.notna(r[metric])]
            result[f'{window}_{metric}'] = float(np.mean(values)) if values else np.nan
    return result


def build_features(games, teams, fixture=None):
    """Generate all features before applying any results from the prediction day."""
    games = games.copy()
    games['game_date'] = pd.to_datetime(games['game_datetime_source']).dt.normalize()
    if fixture is not None:
        day = pd.Timestamp(fixture['game_date']).normalize()
        games = games.loc[games['game_date'] < day].copy()
        row = {'game_id': 'fixture', 'game_date': day, 'game_datetime_source': str(day),
               'season_start': fixture['season_start'], 'home_team_id': str(fixture['home_team_id']),
               'away_team_id': str(fixture['away_team_id']), 'home_win': np.nan, 'split': 'forecast'}
        games = pd.concat([games, pd.DataFrame([row])], ignore_index=True)
    games = games.sort_values(['game_date', 'game_id'])
    if games[['game_date', 'season_start', 'home_team_id', 'away_team_id']].isna().any().any():
        raise ValueError('Missing game date, season or team identifiers.')
    statistics = {(str(r['game_id']), str(r['team_id'])): r for r in teams.to_dict('records')}
    histories = defaultdict(list)
    last_day, elo = {}, {}
    previous_season = None
    rows = []
    for day, daily in games.groupby('game_date', sort=True):
        if daily['season_start'].nunique() != 1:
            raise ValueError('Overlapping season labels on one date.')
        season = int(daily['season_start'].iloc[0])
        if previous_season is not None and season != previous_season:
            elo = {team: 1500 + 0.75 * (rating - 1500) for team, rating in elo.items()}
        previous_season = season
        pending = []
        for game in daily.to_dict('records'):
            gid, home, away = str(game['game_id']), str(game['home_team_id']), str(game['away_team_id'])
            home_history, away_history = histories[(season, home)], histories[(season, away)]
            h, a = summarize(home_history), summarize(away_history)
            latest = [last_day[t] for t in (home, away) if t in last_day]
            assert all(value < day for value in latest)
            difference = elo.get(home, 1500) - elo.get(away, 1500)
            expected = 1 / (1 + 10 ** (-(difference + 65) / 400))
            row = {k: game[k] for k in ('game_id', 'season_start', 'home_team_id', 'away_team_id', 'home_win', 'split')}
            row.update(game_date=day, latest_history_date=max(latest) if latest else pd.NaT,
                       elo_probability=expected, elo_difference=difference,
                       home_games_played=len(home_history), away_games_played=len(away_history))
            row.update({'diff_' + key: h[key] - a[key] for key in h})
            for side, team in [('home', home), ('away', away)]:
                days = (day - last_day[team]).days if team in last_day else None
                row[side + '_rest_days'] = min(days, 14) if days is not None else np.nan
                row[side + '_back_to_back'] = int(days == 1) if days is not None else np.nan
            rows.append(row)
            if pd.notna(game['home_win']):
                pending.append((game, home, away, expected))
        # A same-day result cannot affect another game's features on that day.
        elo_changes = defaultdict(float)
        for game, home, away, expected in pending:
            gid, won = str(game['game_id']), int(game['home_win'])
            if (gid, home) not in statistics or (gid, away) not in statistics:
                raise ValueError(f'Missing team box score for {gid}')
            ht, at = statistics[(gid, home)], statistics[(gid, away)]
            histories[(season, home)].append(team_observation(ht, at, won))
            histories[(season, away)].append(team_observation(at, ht, 1 - won))
            last_day[home] = last_day[away] = day
            delta = 20 * (won - expected)
            elo_changes[home] += delta
            elo_changes[away] -= delta
        for team, delta in elo_changes.items():
            elo[team] = elo.get(team, 1500) + delta
    return pd.DataFrame(rows)


def metrics(y, probabilities):
    p = np.asarray(probabilities, dtype=float)
    return {'accuracy': float(accuracy_score(y, p >= 0.5)),
            'log_loss': float(log_loss(y, p, labels=[0, 1])),
            'brier_score': float(brier_score_loss(y, p)),
            'roc_auc': float(roc_auc_score(y, p))}


def candidates():
    result = {}
    for c in (0.1, 1.0, 10.0):
        result[f'logistic_C{c:g}'] = make_pipeline(
            SimpleImputer(strategy='median', add_indicator=True, keep_empty_features=True),
            StandardScaler(), LogisticRegression(C=c, max_iter=2000, random_state=SEED))
    result['random_forest'] = make_pipeline(
        SimpleImputer(strategy='median', add_indicator=True, keep_empty_features=True),
        RandomForestClassifier(n_estimators=300, max_depth=10, min_samples_leaf=15,
                               max_features='sqrt', random_state=SEED, n_jobs=2))
    for regularization in (1.0, 10.0):
        result[f'gradient_boosting_l2_{regularization:g}'] = make_pipeline(
            SimpleImputer(strategy='median', add_indicator=True, keep_empty_features=True),
            HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_depth=3,
                                           l2_regularization=regularization, early_stopping=False,
                                           random_state=SEED))
    return result


def write_feature_dictionary(output):
    rows = []
    for feature in FEATURES:
        if feature.startswith('diff_'):
            _, window, metric = feature.split('_', 2)
            scope = {'last5': 'last 5 games', 'last10': 'last 10 games', 'season': 'all earlier games'}[window]
            description = f'Home minus away mean {metric}, using {scope} in the same season.'
        elif feature.endswith('games_played'):
            description = 'Number of earlier games for this team in the current season.'
        elif feature.endswith('rest_days'):
            description = 'Calendar days since the last game, capped at 14; empty without history.'
        elif feature.endswith('back_to_back'):
            description = '1 if this team played on the previous day, 0 otherwise; empty without history.'
        else:
            description = 'Home minus away Elo before this day; K=20, home advantage=65, season retention=0.75.'
        rows.append({'feature': feature, 'description': description,
                     'cutoff': 'Earlier source calendar days only; no current-day results.'})
    pd.DataFrame(rows).to_csv(output / 'feature_dictionary.csv', index=False)


def save_plots(y, predictions, importance, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from sklearn.calibration import calibration_curve
    from sklearn.metrics import roc_curve

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for name, probabilities in predictions.items():
        observed, predicted = calibration_curve(y, probabilities, n_bins=10, strategy='quantile')
        axes[0].plot(predicted, observed, marker='o', label=name)
        fpr, tpr, _ = roc_curve(y, probabilities)
        axes[1].plot(fpr, tpr, label=name)
    axes[0].plot([0, 1], [0, 1], '--', color='gray')
    axes[0].set(xlabel='Predicted home-win probability', ylabel='Observed home-win rate', title='Test calibration')
    axes[1].plot([0, 1], [0, 1], '--', color='gray')
    axes[1].set(xlabel='False positive rate', ylabel='True positive rate', title='Test ROC')
    for axis in axes:
        axis.legend(fontsize=8)
        axis.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output / 'test_calibration_roc.png', dpi=160)
    plt.close(fig)
    top = importance.head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(top['feature'], top['importance_mean'], xerr=top['importance_std'])
    ax.set(xlabel='Increase in validation log loss when shuffled', title='Validation permutation importance')
    fig.tight_layout()
    fig.savefig(output / 'validation_feature_importance.png', dpi=160)
    plt.close(fig)


def write_report(report, output):
    lines = ['# Pregame result prediction', '',
             f"Selected model: **{report['selected_model']}**, chosen by validation log loss.", '',
             'The target is the probability that the home team wins. A probability of 0.5 is the classification threshold.', '',
             '## Chronological split', '', '| Split | Games | First date | Last date |', '| --- | ---: | --- | --- |']
    for split, values in report['splits'].items():
        lines.append(f"| {split} | {values['games']} | {values['first_date']} | {values['last_date']} |")
    for label, scores in [('Validation model comparison', report['validation']), ('Held-out test', report['test'])]:
        lines += ['', '## ' + label, '', '| Model | Accuracy | Log loss | Brier score | ROC-AUC |',
                  '| --- | ---: | ---: | ---: | ---: |']
        for name, values in sorted(scores.items(), key=lambda item: item[1]['log_loss']):
            lines.append(f"| {name} | {values['accuracy']:.3f} | {values['log_loss']:.3f} | {values['brier_score']:.3f} | {values['roc_auc']:.3f} |")
    lines += ['', '## Evaluation rules', '',
              '- Use only games from earlier calendar days to build features. Exclude all same-day results.',
              '- Reset rolling and cumulative statistics each season. Carry Elo across seasons with 25% regression to 1500.',
              '- Fit imputation and scaling on training data inside each model pipeline.',
              '- Select the learned model using validation only, then refit it on training plus validation.',
              '- Freeze model weights for testing. Update histories with earlier test-day results, as in daily forecasting.',
              '- Evaluate the selected model and fixed baselines on the test set. Do not use test scores to select a new model.',
              '- Estimate feature importance on validation before the final refit.', '',
              '## Limits', '',
              '- This is a retrospective daily forecast, not a live betting or deployment system.',
              '- Missing source games shorten histories. Source snapshots may include later corrections.',
              '- The dataset does not identify neutral venues reliably. Home advantage is approximate, including the 2019–20 bubble.',
              '- Injuries are excluded because publication and game timezones have not been verified.',
              '- Possessions use a box-score approximation. Player transfers and expected lineups are not modeled directly.',
              '- Point estimates describe one held-out season. They do not establish performance in future seasons.',
              '- Correlated statistics can share permutation importance; these values do not establish causation.', '',
              '## Figures', '', '![Test calibration and ROC](test_calibration_roc.png)', '',
              '![Validation feature importance](validation_feature_importance.png)', '']
    (output / 'RESULTS.md').write_text('\n'.join(lines))


def train(args):
    if args.output.exists():
        raise FileExistsError('Choose a new output directory to preserve the previous experiment.')
    args.output.mkdir(parents=True)
    games, teams = load_history(args.input)
    print('Building features from earlier days...', flush=True)
    frame = build_features(games, teams)
    frame.to_csv(args.output / 'game_features.csv', index=False)
    write_feature_dictionary(args.output)
    parts = {split: frame.loc[frame['split'] == split].copy() for split in ('train', 'validation', 'test')}
    for split, part in parts.items():
        if part.empty or part['home_win'].nunique() != 2:
            raise ValueError(f'{split} needs games from both classes.')
    if not (parts['train']['game_date'].max() < parts['validation']['game_date'].min()
            and parts['validation']['game_date'].max() < parts['test']['game_date'].min()):
        raise ValueError('Splits overlap in time.')
    training, validation, test = (parts[s] for s in ('train', 'validation', 'test'))
    x_train, y_train = training[FEATURES], training['home_win'].astype(int)
    x_valid, y_valid = validation[FEATURES], validation['home_win'].astype(int)
    x_test, y_test = test[FEATURES], test['home_win'].astype(int)
    validation_scores = {
        'home_prior': metrics(y_valid, np.full(len(validation), y_train.mean())),
        'elo': metrics(y_valid, validation['elo_probability']),
    }
    models = candidates()
    for name, model in models.items():
        print('Training ' + name + '...', flush=True)
        model.fit(x_train, y_train)
        validation_scores[name] = metrics(y_valid, model.predict_proba(x_valid)[:, 1])
    selected = min(models, key=lambda name: validation_scores[name]['log_loss'])
    print('Selected on validation: ' + selected, flush=True)
    permutation = permutation_importance(models[selected], x_valid, y_valid, scoring='neg_log_loss',
                                         n_repeats=5, random_state=SEED, n_jobs=1)
    importance = pd.DataFrame({'feature': FEATURES, 'importance_mean': permutation.importances_mean,
                               'importance_std': permutation.importances_std}).sort_values('importance_mean', ascending=False)
    importance.to_csv(args.output / 'validation_feature_importance.csv', index=False)
    combined = pd.concat([training, validation], ignore_index=True)
    estimator = clone(models[selected]).fit(combined[FEATURES], combined['home_win'].astype(int))
    predictions = {
        selected: estimator.predict_proba(x_test)[:, 1],
        'home_prior': np.full(len(test), combined['home_win'].mean()),
        'elo': test['elo_probability'].to_numpy(),
    }
    test_scores = {name: metrics(y_test, p) for name, p in predictions.items()}
    output_predictions = test[['game_id', 'game_date', 'home_team_id', 'away_team_id', 'home_win']].copy()
    for name, p in predictions.items():
        output_predictions['probability_' + name] = p
    output_predictions['predicted_home_win'] = (predictions[selected] >= 0.5).astype(int)
    output_predictions.to_csv(args.output / 'test_predictions.csv', index=False)
    packages = {}
    from importlib.metadata import version
    for name in ('numpy', 'pandas', 'scikit-learn', 'joblib', 'matplotlib'):
        packages[name] = version(name)
    fingerprints = {}
    for name in ('games.csv', 'team_games.csv', 'quality_report.json'):
        with (args.input / name).open('rb') as stream:
            fingerprints[name] = hashlib.file_digest(stream, 'sha256').hexdigest()
    report = {'selected_model': selected, 'selection_rule': 'Minimum validation log loss among learned candidates',
              'input_directory': str(args.input),
              'seed': SEED, 'feature_version': VERSION, 'features': FEATURES,
              'splits': {s: {'games': len(p), 'first_date': str(p['game_date'].min().date()),
                             'last_date': str(p['game_date'].max().date())} for s, p in parts.items()},
              'validation': validation_scores, 'test': test_scores, 'packages': packages,
              'input_sha256': fingerprints, 'candidate_parameters': {n: str(m) for n, m in models.items()}}
    (args.output / 'metrics.json').write_text(json.dumps(report, indent=2) + '\n')
    (args.output / 'input_quality_report.json').write_bytes((args.input / 'quality_report.json').read_bytes())
    artifact = {'model': estimator, 'features': FEATURES, 'feature_version': VERSION,
                'selected_model': selected, 'trained_through': str(combined['game_date'].max().date()),
                'input_sha256': fingerprints, 'packages': packages}
    joblib.dump(artifact, args.output / 'model.joblib')
    # Check that the persisted model reproduces the tested probabilities.
    restored = joblib.load(args.output / 'model.joblib')
    np.testing.assert_allclose(restored['model'].predict_proba(x_test)[:, 1], predictions[selected])
    save_plots(y_test, predictions, importance, args.output)
    write_report(report, args.output)
    (args.output / '_SUCCESS').write_text('Features, model, metrics and artifact round-trip verified.\n')
    print(json.dumps({'selected_model': selected, 'test': test_scores}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path('data/processed'))
    parser.add_argument('--output', type=Path, default=Path('reports/result_prediction'))
    arguments = parser.parse_args()
    with threadpool_limits(limits=2):
        train(arguments)
