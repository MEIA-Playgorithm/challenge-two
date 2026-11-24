"""Temporal player-production and starting-lineup evaluation (Element 3)."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction import DictVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

TARGETS = ['points', 'rebounds_total', 'assists']
HISTORY = TARGETS + ['steals', 'blocks', 'turnovers', 'field_goals_attempted']


def player_features(players, games):
    """Read each calendar day's outcomes only after making that day's features."""
    data = players.merge(games[['game_id', 'split']], on='game_id', validate='many_to_one')
    data = data[data.participation_status.eq('played')].copy()
    data['day'] = pd.to_datetime(data.game_date).dt.normalize()
    history = defaultdict(lambda: deque(maxlen=10))
    rows = []
    for day, group in data.sort_values(['day', 'game_id', 'player_id']).groupby('day', sort=True):
        for r in group.itertuples(index=False):
            past = history[(r.player_id, r.season_start)]
            if len(past) < 5 or any(pd.isna(getattr(r, c)) for c in TARGETS):
                continue
            row = dict(game_id=r.game_id, player_id=r.player_id, team_id=r.team_id,
                       game_date=str(day.date()), season_start=r.season_start, split=r.split,
                       name=f'{r.first_name} {r.last_name}', home=int(r.home), history_count=len(past),
                       rest_days=min((day - past[-1][0]).days, 30))
            values = np.array([v for _, v in past], dtype=float)
            for i, c in enumerate(HISTORY):
                for window in (5, 10):
                    row[f'{c}_last{window}'] = float(np.nanmean(values[-window:, i]))
            row.update({c: float(getattr(r, c)) for c in TARGETS})
            rows.append(row)
        for r in group.itertuples(index=False):
            history[(r.player_id, r.season_start)].append((day, [getattr(r, c) for c in HISTORY]))
    return pd.DataFrame(rows)


def lineup_features(home, away, include_quintet=True):
    features = {f'player:{p}': 1.0 for p in home}
    features.update({f'player:{p}': -1.0 for p in away})
    if include_quintet:
        features['five:' + '|'.join(sorted(home))] = 1.0
        features['five:' + '|'.join(sorted(away))] = -1.0
    return features


def starting_lineups(players, games):
    starters = players[players.starting_position.fillna('').str.strip().ne('')]
    groups = {key: tuple(sorted(g.player_id)) for key, g in starters.groupby(['game_id', 'team_id'])}
    accepted, rejected = [], []
    for r in games.sort_values(['game_date', 'game_id']).itertuples(index=False):
        home = groups.get((r.game_id, r.home_team_id), ())
        away = groups.get((r.game_id, r.away_team_id), ())
        valid = len(home) == len(set(home)) == len(away) == len(set(away)) == 5 and not set(home) & set(away)
        if not valid:
            rejected.append(dict(game_id=r.game_id, season_start=r.season_start,
                                 home_starters=len(home), away_starters=len(away), reason='incomplete_or_invalid_starters'))
            continue
        accepted.append(dict(game_id=r.game_id, game_date=r.game_date, season_start=r.season_start,
                             split=r.split, home_team_id=r.home_team_id, away_team_id=r.away_team_id,
                             home=home, away=away, margin=float(r.home_score-r.away_score)))
    return pd.DataFrame(accepted), pd.DataFrame(rejected)


def scores(y, prediction):
    return {'mae': float(mean_absolute_error(y, prediction)),
            'rmse': float(np.sqrt(mean_squared_error(y, prediction))),
            'r2': float(r2_score(y, prediction))}


def player_model(name):
    if name == 'forest':
        return make_pipeline(SimpleImputer(), RandomForestRegressor(
            n_estimators=80, max_depth=12, min_samples_leaf=30, max_features=.8,
            n_jobs=2, random_state=42))
    return make_pipeline(SimpleImputer(), StandardScaler(), Ridge(alpha=float(name.split('_')[1])))


def train_players(frame, output):
    columns = ['home', 'history_count', 'rest_days'] + [f'{c}_last{w}' for c in HISTORY for w in (5, 10)]
    train, val, test = [frame[frame.split.eq(s)] for s in ('train', 'validation', 'test')]
    results = {}
    for name in ('ridge_1', 'ridge_100', 'forest'):
        model = player_model(name).fit(train[columns], train[TARGETS])
        results[name] = scores(val[TARGETS], model.predict(val[columns]))
    results['last10_mean'] = scores(val[TARGETS], val[[c+'_last10' for c in TARGETS]])
    selected = min(results, key=lambda k: results[k]['mae'])
    fit = pd.concat([train, val])
    model = None if selected == 'last10_mean' else player_model(selected).fit(fit[columns], fit[TARGETS])
    pred = test[[c+'_last10' for c in TARGETS]].to_numpy() if model is None else model.predict(test[columns])
    baseline = test[[c+'_last10' for c in TARGETS]].to_numpy()
    metrics = {'selected': selected, 'selection_metric': 'validation macro MAE',
               'counts': {s: int(frame.split.eq(s).sum()) for s in ('train', 'validation', 'test')},
               'validation': results, 'test': {c: scores(test[c], pred[:, i]) for i, c in enumerate(TARGETS)},
               'test_baseline': {c: scores(test[c], baseline[:, i]) for i, c in enumerate(TARGETS)}}
    predictions = test[['game_id', 'player_id', 'name', 'game_date', 'team_id']+TARGETS].copy()
    for i, c in enumerate(TARGETS):
        predictions[c+'_predicted'] = pred[:, i]
        predictions[c+'_baseline'] = baseline[:, i]
        predictions[c+'_residual'] = predictions[c] - pred[:, i]
    predictions.to_csv(output/'player_test_predictions.csv', index=False)
    summary = predictions.groupby(['player_id', 'name']).agg(
        games=('game_id', 'size'), points=('points', 'mean'), rebounds=('rebounds_total', 'mean'),
        assists=('assists', 'mean'), points_above_expectation=('points_residual', 'mean'))
    summary['eligible_20_games'] = summary.games.ge(20)
    summary.to_csv(output/'player_test_summary.csv')
    joblib.dump({'model': model, 'features': columns, 'targets': TARGETS, 'selected': selected}, output/'player_model.joblib')
    return metrics


def train_lineups(frame, output):
    train, val, test = [frame[frame.split.eq(s)] for s in ('train', 'validation', 'test')]
    results = {}
    for quintets in (False, True):
        vectorizer = DictVectorizer()
        x = vectorizer.fit_transform([lineup_features(r.home, r.away, quintets) for r in train.itertuples()])
        xv = vectorizer.transform([lineup_features(r.home, r.away, quintets) for r in val.itertuples()])
        for alpha in (10., 100., 1000.):
            model = Ridge(alpha=alpha, solver='lsqr').fit(x, train.margin)
            results[f'{int(quintets)}_{alpha}'] = scores(val.margin, model.predict(xv))
    results['home_mean'] = scores(val.margin, np.full(len(val), train.margin.mean()))
    selected = min(results, key=lambda k: results[k]['rmse'])
    fit = pd.concat([train, val])
    quintets = selected.startswith('1_')
    vectorizer = DictVectorizer()
    x = vectorizer.fit_transform([lineup_features(r.home, r.away, quintets) for r in fit.itertuples()])
    model = None if selected == 'home_mean' else Ridge(alpha=float(selected.split('_')[1]), solver='lsqr').fit(x, fit.margin)
    xt = vectorizer.transform([lineup_features(r.home, r.away, quintets) for r in test.itertuples()])
    pred = np.full(len(test), fit.margin.mean()) if model is None else model.predict(xt)
    baseline = np.full(len(test), fit.margin.mean())
    prediction = test.drop(columns=['home', 'away']).copy()
    prediction['predicted_margin'] = pred
    prediction['baseline_margin'] = baseline
    prediction.to_csv(output/'lineup_test_predictions.csv', index=False)
    effects = {} if model is None else dict(zip(vectorizer.get_feature_names_out(), model.coef_))
    pd.DataFrame([{'feature': k, 'association_points': float(v)} for k, v in effects.items()],
                 columns=['feature', 'association_points']).to_csv(output/'lineup_coefficients.csv', index=False)
    records = []
    known_players = {p for r in fit.itertuples() for p in r.home+r.away}
    unknown = sum(p not in known_players for r in test.itertuples() for p in r.home+r.away)
    for r in test.itertuples():
        for side, sign in [('home', 1), ('away', -1)]:
            players = getattr(r, side)
            key = '|'.join(players)
            records.append(dict(team_id=getattr(r, side+'_team_id'), lineup=key, game_margin=sign*r.margin,
                                association_points=sum(effects.get('player:'+p, 0) for p in players)+effects.get('five:'+key, 0)))
    summary = pd.DataFrame(records).groupby(['team_id', 'lineup']).agg(
        games=('game_margin', 'size'), mean_game_margin=('game_margin', 'mean'),
        association_points=('association_points', 'first'))
    summary['eligible_10_games'] = summary.games.ge(10)
    summary.to_csv(output/'starting_lineup_test_summary.csv')
    joblib.dump({'model': model, 'vectorizer': vectorizer, 'include_quintet': quintets,
                 'baseline': float(fit.margin.mean()), 'selected': selected}, output/'lineup_model.joblib')
    return {'selected': selected, 'selection_metric': 'validation RMSE', 'validation': results,
            'counts': {s: int(frame.split.eq(s).sum()) for s in ('train', 'validation', 'test')},
            'test': scores(test.margin, pred), 'test_baseline': scores(test.margin, baseline),
            'unknown_test_player_slots': unknown}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path('data/processed'))
    parser.add_argument('--output-dir', type=Path, default=Path('reports/performance'))
    args = parser.parse_args()
    if not (args.data_dir/'_SUCCESS').exists():
        raise ValueError('Prepared data must have a _SUCCESS marker')
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    (output/'_SUCCESS').unlink(missing_ok=True)
    ids = {c: str for c in ('game_id', 'player_id', 'team_id', 'home_team_id', 'away_team_id', 'opponent_team_id')}
    games = pd.read_csv(args.data_dir/'games.csv', dtype=ids)
    players = pd.read_csv(args.data_dir/'player_games.csv', dtype=ids, low_memory=False)
    if players.duplicated(['game_id', 'player_id']).any():
        raise ValueError('Duplicate player-game records')
    print('Building prior-day player histories...', flush=True)
    features = player_features(players, games)
    print('Training player models...', flush=True)
    player_metrics = train_players(features, output)
    lineups, rejected = starting_lineups(players, games)
    rejected.to_csv(output/'excluded_lineup_games.csv', index=False)
    print('Training starting-lineup models...', flush=True)
    lineup_metrics = train_lineups(lineups, output)
    coverage = games.groupby('season_start').size().rename('games').to_frame()
    coverage['accepted_lineup_games'] = lineups.groupby('season_start').size()
    coverage['excluded_lineup_games'] = coverage.games - coverage.accepted_lineup_games
    coverage.to_csv(output/'lineup_coverage.csv')
    metrics = {'players': player_metrics, 'starting_lineups': lineup_metrics,
               'input_sha256': {n: hashlib.sha256((args.data_dir/n).read_bytes()).hexdigest()
                                for n in ('games.csv', 'player_games.csv')},
               'seed': 42, 'scope': 'Players conditional on playing; starting lineups evaluated by full-game margin'}
    (output/'metrics.json').write_text(json.dumps(metrics, indent=2)+'\n')
    report = ['# Player and starting-lineup results', '',
              'We select models on 2024–25 and evaluate once on 2025–26. Training uses 2019–20 through 2023–24.', '',
              f"Player model: `{player_metrics['selected']}`. Errors are in each statistic's units.", '',
              '| Target | Test MAE | Last-10 baseline MAE |', '| --- | ---: | ---: |']
    for c in TARGETS:
        report.append(f"| {c} | {player_metrics['test'][c]['mae']:.3f} | {player_metrics['test_baseline'][c]['mae']:.3f} |")
    report += ['', f"Starting-lineup model: `{lineup_metrics['selected']}`.",
               f"Test margin RMSE: {lineup_metrics['test']['rmse']:.3f} points; home-mean baseline: {lineup_metrics['test_baseline']['rmse']:.3f}.", '',
               f'Accepted {len(lineups):,} games; excluded {len(rejected):,} games with invalid or missing starters.', '',
               'These are associations with full-game outcomes, not estimates of shared on-court performance.',
               'Bench players, opponents and coaching affect these outcomes. Coefficients do not establish individual causal value.',
               'Player predictions assume participation and at least five earlier appearances in the season.',
               'Observed starters are supplied retrospectively; availability before tip-off is not verified.', '',
               'See [the method guide](../../docs/PERFORMANCE_EVALUATION.md) for definitions and reproducible commands.']
    (output/'RESULTS.md').write_text('\n'.join(report)+'\n')
    (output/'_SUCCESS').write_text('Completed player and starting-lineup evaluation.\n')
    print(json.dumps({'players': player_metrics, 'lineups': lineup_metrics}, indent=2), flush=True)


if __name__ == '__main__':
    main()
