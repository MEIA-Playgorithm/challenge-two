"""Plan a starting five and a feasible 48-minute rotation with CP-SAT."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from ortools.sat.python import cp_model

from train_performance import player_features, TARGETS

ROLES = ('G1', 'G2', 'F1', 'F2', 'C')


def build_roster(data_dir, model_dir, team_id, date, home=True, lookback_days=30):
    """Build a candidate pool and predictions without reading outcomes on/after date."""
    day = pd.Timestamp(date).normalize()
    metrics = json.loads((model_dir/'metrics.json').read_text())
    # Element 3's final models include the validation season through 2024–25.
    games = pd.read_csv(data_dir/'games.csv', dtype={'game_id': str})
    fit_end = pd.to_datetime(games.loc[games.split.isin(['train', 'validation']), 'game_date']).max().normalize()
    if day <= fit_end:
        raise ValueError(f'The saved ML models require a date after {fit_end.date()}')
    for name, expected in metrics['input_sha256'].items():
        if hashlib.sha256((data_dir/name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'{name} differs from the data used to train the ML models')
    p = pd.read_csv(data_dir/'player_games.csv', dtype={'game_id': str, 'player_id': str, 'team_id': str}, low_memory=False)
    p['day'] = pd.to_datetime(p.game_date).dt.normalize()
    past = p[p.day.lt(day)].copy()
    latest = past.sort_values(['day', 'game_id']).drop_duplicates('player_id', keep='last')
    latest = latest[latest.team_id.eq(team_id) & latest.day.ge(day-pd.Timedelta(days=lookback_days))]
    if latest.empty:
        raise ValueError('No recent candidate roster for this team and date')
    # Infer the season from the latest earlier game, never from future outcomes.
    season = int(past.season_start.max())
    latest = latest[latest.season_start.eq(season)]
    synthetic = latest.copy()
    synthetic['game_id'] = 'planning'
    synthetic['game_date'] = str(day)
    synthetic['participation_status'] = 'played'
    synthetic['home'] = int(home)
    synthetic[TARGETS] = 0.0  # Targets are placeholders; never passed to the estimator.
    relevant = past[past.player_id.isin(latest.player_id) & past.season_start.eq(season)]
    feature_games = pd.concat([games[['game_id', 'split']], pd.DataFrame([{'game_id': 'planning', 'split': 'planning'}])])
    features = player_features(pd.concat([relevant, synthetic], ignore_index=True), feature_games)
    if features.empty:
        raise ValueError('No candidates have five earlier appearances in the season')
    features = features[features.game_id.eq('planning')].copy()
    bundle = joblib.load(model_dir/'player_model.joblib')
    if not features.empty:
        predictions = (features[[c+'_last10' for c in TARGETS]].to_numpy() if bundle['model'] is None
                       else bundle['model'].predict(features[bundle['features']]))
    else:
        predictions = np.empty((0, 3))
    predicted = {r.player_id: values for r, values in zip(features.itertuples(), predictions)}
    bio = pd.read_csv(data_dir/'players.csv', dtype={'player_id': str}).set_index('player_id')
    lineup = joblib.load(model_dir/'lineup_model.joblib')
    if lineup['include_quintet']:
        raise ValueError('This planner supports the selected additive starter model only')
    effects = ({} if lineup['model'] is None else dict(zip(lineup['vectorizer'].get_feature_names_out(), lineup['model'].coef_)))
    roster, excluded = [], []
    for r in latest.sort_values('player_id').itertuples():
        roles = [role for role, field in [('G', 'guard'), ('F', 'forward'), ('C', 'center')]
                 if r.player_id in bio.index and bio.loc[r.player_id, field] == 1]
        if r.player_id not in predicted or not roles:
            excluded.append({'player_id': r.player_id, 'name': f'{r.first_name} {r.last_name}',
                             'reason': 'insufficient_history' if r.player_id not in predicted else 'unknown_position'})
            continue
        values = np.maximum(predicted[r.player_id], 0)
        roster.append(dict(player_id=r.player_id, name=f'{r.first_name} {r.last_name}', roles=roles,
                           available=True, min_minutes=8, max_minutes=36, force_starter=False,
                           predictions=dict(zip(TARGETS, map(float, values))),
                           starter_association=float(effects.get('player:'+r.player_id, 0)),
                           starter_known='player:'+r.player_id in effects,
                           last_record_date=str(r.day.date())))
    return {'team_id': team_id, 'date': str(day.date()), 'home': home, 'block_minutes': 4,
            'min_rotation': 8, 'max_rotation': 10, 'max_consecutive_blocks': 3,
            'weights': {'points': 1.0, 'rebounds_total': 1.2, 'assists': 1.5},
            'starter_weight': 1.0, 'players': roster, 'excluded_candidates': excluded,
            'provenance': {'model_fit_end': str(fit_end.date()), 'lookback_days': lookback_days,
                           'availability': 'assumed; confirm or override before operational use',
                           'positions': 'biography snapshot; not a verified historical position roster',
                           'input_sha256': metrics['input_sha256'],
                           'model_sha256': {n: hashlib.sha256((model_dir/n).read_bytes()).hexdigest()
                                            for n in ['player_model.joblib', 'lineup_model.joblib']}}}


def validate_config(config):
    block = config['block_minutes']
    if not isinstance(block, int) or block <= 0 or 12 % block:
        raise ValueError('block_minutes must be a positive integer divisor of 12')
    players = config['players']
    if len({p['player_id'] for p in players}) != len(players):
        raise ValueError('Duplicate player IDs')
    if any(not isinstance(config[k], int) for k in ('min_rotation', 'max_rotation', 'max_consecutive_blocks')):
        raise ValueError('Rotation and consecutive-block limits must be integers')
    if set(config['weights']) != set(TARGETS):
        raise ValueError('Provide weights for points, rebounds_total and assists')
    if not 5 <= config['min_rotation'] <= config['max_rotation'] <= len(players):
        raise ValueError('Require 5 <= min_rotation <= max_rotation <= roster size')
    if not 1 <= config['max_consecutive_blocks'] <= 48//block:
        raise ValueError('Invalid consecutive-block limit')
    for p in players:
        if not p['roles'] or not set(p['roles']) <= {'G', 'F', 'C'}:
            raise ValueError('Each player needs valid G/F/C roles')
        if any(not isinstance(p[k], int) for k in ('min_minutes', 'max_minutes')):
            raise ValueError('Minute limits must be integers')
        if set(p['predictions']) != set(TARGETS):
            raise ValueError('Provide all three statistical predictions')
        if not 0 <= p['min_minutes'] <= p['max_minutes'] <= 48:
            raise ValueError('Invalid minute bounds')
        if p['min_minutes'] % block or p['max_minutes'] % block:
            raise ValueError('Minute bounds must be multiples of block_minutes')
        if not isinstance(p['available'], bool) or not isinstance(p.get('force_starter', False), bool):
            raise ValueError('Availability and starter flags must be booleans')
        values = [*p['predictions'].values(), p['starter_association'], *config['weights'].values(), config['starter_weight']]
        if not all(np.isfinite(v) for v in values):
            raise ValueError('Scores and weights must be finite')


def solve(config, time_limit=30):
    validate_config(config)
    players = config['players']
    block = config['block_minutes']
    slots = 48//block
    model = cp_model.CpModel()
    on = {(i,t): model.new_bool_var(f'on_{i}_{t}') for i in range(len(players)) for t in range(slots)}
    used = [model.new_bool_var(f'used_{i}') for i in range(len(players))]
    role_vars = {}
    for t in range(slots):
        for role in ROLES:
            eligible = []
            for i,p in enumerate(players):
                if role[0] in p['roles']:
                    v = model.new_bool_var(f'role_{i}_{t}_{role}')
                    role_vars[i,t,role] = v
                    eligible.append(v)
            model.add(sum(eligible) == 1)
        for i,p in enumerate(players):
            model.add(sum(role_vars[i,t,r] for r in ROLES if (i,t,r) in role_vars) == on[i,t])
        model.add(sum(on[i,t] for i in range(len(players))) == 5)
    for i,p in enumerate(players):
        total = sum(on[i,t] for t in range(slots))
        model.add(total >= max(1, p['min_minutes']//block)*used[i])
        model.add(total <= (p['max_minutes']//block)*used[i])
        if not p['available']:
            model.add(used[i] == 0)
        if p.get('force_starter', False):
            model.add(on[i,0] == 1)
        consecutive = config['max_consecutive_blocks']
        for t in range(slots-consecutive):
            model.add(sum(on[i,s] for s in range(t,t+consecutive+1)) <= consecutive)
    model.add(sum(used) >= config['min_rotation'])
    model.add(sum(used) <= config['max_rotation'])
    # Integer utility: weighted production exposure plus an additive starter association.
    scores, objective = [], []
    for i,p in enumerate(players):
        utility = sum(config['weights'][c]*p['predictions'][c] for c in TARGETS)
        scores.append(utility)
        exposure = round(1000*utility*block/48)
        starter = round(1000*config['starter_weight']*p['starter_association'])
        objective += [exposure*on[i,t] for t in range(slots)] + [starter*on[i,0]]
    model.maximize(sum(objective))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 42
    status = solver.solve(model)
    result = {'status': solver.status_name(status), 'wall_time_seconds': solver.wall_time,
              'score_definition': 'Weighted predicted production times minute share plus starting-five association; planning utility, not predicted points or wins'}
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result['message'] = 'No feasible plan returned. Check available positions, minute capacity, rotation size, forced starters and rest limits.'
        return result
    result.update(objective=solver.objective_value/1000, best_bound=solver.best_objective_bound/1000)
    result['schedule'] = []
    for t in range(slots):
        assignment = {role: players[i]['player_id'] for (i,s,role),v in role_vars.items()
                      if s == t and solver.value(v)}
        result['schedule'].append({'block': t, 'quarter': (t*block)//12+1,
                                   'start_minute': t*block, 'end_minute': (t+1)*block, **assignment})
    result['players'] = [dict(player_id=p['player_id'], name=p['name'],
                              minutes=block*sum(solver.value(on[i,t]) for t in range(slots)),
                              starter=bool(solver.value(on[i,0])), utility=scores[i],
                              starter_association=p['starter_association']) for i,p in enumerate(players)]
    verify_solution(config, result)
    result['constraints_verified'] = True
    return result


def verify_solution(config, result):
    """Independent checks on the exported schedule, not solver variables."""
    players = {p['player_id']: p for p in config['players']}
    block = config['block_minutes']
    counts = {p: 0 for p in players}
    streak = counts.copy()
    assert len(result['schedule']) == 48//block
    for t,row in enumerate(result['schedule']):
        active = [row[r] for r in ROLES]
        assert len(set(active)) == 5
        assert row['start_minute'] == t*block and row['end_minute'] == (t+1)*block
        for role in ROLES:
            assert players[row[role]]['available'] and role[0] in players[row[role]]['roles']
        for pid in players:
            counts[pid] += block if pid in active else 0
            streak[pid] = streak[pid]+1 if pid in active else 0
            assert streak[pid] <= config['max_consecutive_blocks']
    assert sum(counts.values()) == 240
    assert config['min_rotation'] <= sum(v>0 for v in counts.values()) <= config['max_rotation']
    for p in result['players']:
        source = players[p['player_id']]
        assert p['minutes'] == counts[p['player_id']]
        assert p['minutes'] == 0 or source['min_minutes'] <= p['minutes'] <= source['max_minutes']
        assert p['starter'] == (p['player_id'] in [result['schedule'][0][r] for r in ROLES])
        assert not source.get('force_starter', False) or p['starter']


def plot_rotation(result, output):
    import os
    os.environ.setdefault('MPLCONFIGDIR', '/tmp/challenge-two-matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    active = sorted([p for p in result['players'] if p['minutes']],
                    key=lambda p: (-p['starter'], -p['minutes'], p['name']))
    figure, axis = plt.subplots(figsize=(12, 5))
    colors = {'G': '#2c7fb8', 'F': '#41ab5d', 'C': '#e79b35'}
    for y,p in enumerate(active):
        for row in result['schedule']:
            for role in ROLES:
                if row[role] == p['player_id']:
                    axis.broken_barh([(row['start_minute'], row['end_minute']-row['start_minute'])],
                                     (y-.35, .7), facecolors=colors[role[0]], edgecolors='white')
    axis.set_yticks(range(len(active)), [f"{p['name']} ({p['minutes']} min)" for p in active])
    axis.invert_yaxis()
    axis.set_xlim(0,48)
    axis.set_xticks(range(0,49,4))
    axis.set_xlabel('Elapsed game minutes')
    axis.set_title('Planned rotation — blue: guard, green: forward, orange: center')
    for x in [12,24,36]:
        axis.axvline(x, color='black', alpha=.4, linestyle='--')
    figure.tight_layout()
    figure.savefig(output/'rotation.png', dpi=160)
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path('data/processed'))
    parser.add_argument('--model-dir', type=Path, default=Path('reports/performance'))
    parser.add_argument('--output-dir', type=Path, default=Path('reports/rotation'))
    parser.add_argument('--team-id', default='1610612738')
    parser.add_argument('--date', default='2026-04-01')
    parser.add_argument('--away', action='store_true')
    parser.add_argument('--config', type=Path, help='Use an edited roster and constraints JSON instead of generating inputs')
    parser.add_argument('--time-limit', type=float, default=30)
    args = parser.parse_args()
    if args.time_limit <= 0:
        parser.error('--time-limit must be positive')
    config = json.loads(args.config.read_text()) if args.config else build_roster(args.data_dir, args.model_dir, args.team_id, args.date, not args.away)
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    # Remove stale successful artifacts before attempting another solve.
    for name in ['_SUCCESS', 'schedule.csv', 'minutes.csv', 'RESULTS.md', 'rotation.png']:
        (output/name).unlink(missing_ok=True)
    (output/'inputs.json').write_text(json.dumps(config, indent=2)+'\n')
    result = solve(config, args.time_limit)
    (output/'solution.json').write_text(json.dumps(result, indent=2)+'\n')
    if 'schedule' not in result:
        print(json.dumps(result, indent=2))
        raise SystemExit(2)
    pd.DataFrame(result['schedule']).to_csv(output/'schedule.csv', index=False)
    pd.DataFrame(result['players']).sort_values(['starter','minutes'], ascending=False).to_csv(output/'minutes.csv', index=False)
    plot_rotation(result, output)
    lines = ['# Starting five and minute plan', '', f"Team: {config['team_id']}. Scenario date: {config['date']}.",
             f"Solver status: **{result['status']}**. Utility: {result['objective']:.3f}; upper bound: {result['best_bound']:.3f}.", '',
             'This retrospective example assumes candidate availability. Confirm the roster before using the plan.',
             'The utility is a planning preference, not a forecast of points, wins or the causal effect of extra minutes.', '',
             '| Player | Starts | Minutes |', '| --- | --- | ---: |']
    for p in sorted(result['players'], key=lambda r: (-r['starter'], -r['minutes'], r['name'])):
        lines.append(f"| {p['name']} | {'Yes' if p['starter'] else 'No'} | {p['minutes']} |")
    lines += ['', '![Planned rotation](rotation.png)', '', 'Total: 240 player-minutes. Every block covers two guard, two forward and one center slot.',
              'The exported schedule passed independent constraint checks.', '',
              'See [the planning guide](../../docs/ROTATION_PLANNING.md) for assumptions and configuration.']
    (output/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    (output/'_SUCCESS').write_text('Feasible rotation exported and independently checked.\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
