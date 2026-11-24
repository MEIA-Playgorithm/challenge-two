#!/usr/bin/env python3
"""Predict one fixture using the saved model and earlier completed games."""

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from threadpoolctl import threadpool_limits

from train_results import VERSION, build_features, load_history


def predict(args):
    artifact = joblib.load(args.model)
    if artifact['feature_version'] != VERSION:
        raise ValueError('The model uses a different feature definition.')
    day = pd.Timestamp(args.date).normalize()
    if day <= pd.Timestamp(artifact['trained_through']):
        raise ValueError('The forecast date must follow the final training date.')
    games, teams = load_history(args.input)
    dates = pd.to_datetime(games['game_datetime_source']).dt.normalize()
    history = games.loc[dates < day]
    if history.empty:
        raise ValueError('No games before the prediction cutoff.')
    known_teams = set(history['home_team_id']) | set(history['away_team_id'])
    if args.home_team_id == args.away_team_id or not {args.home_team_id, args.away_team_id} <= known_teams:
        raise ValueError('Use two distinct team IDs present in the historical data.')
    last_season = int(history['season_start'].max())
    if args.season_start not in (last_season, last_season + 1):
        raise ValueError('Use the last observed season or the following season; update older histories first.')
    fixture = {'game_date': str(day.date()), 'home_team_id': args.home_team_id,
               'away_team_id': args.away_team_id, 'season_start': args.season_start}
    rows = build_features(games, teams, fixture=fixture)
    row = rows.loc[rows['game_id'] == 'fixture', artifact['features']]
    probability = float(artifact['model'].predict_proba(row)[0, 1])
    latest = pd.to_datetime(history['game_datetime_source']).dt.normalize().max()
    result = {**fixture, 'home_win_probability': probability, 'away_win_probability': 1 - probability,
              'model': artifact['selected_model'], 'model_trained_through': artifact['trained_through'],
              'latest_history_date': str(latest.date()), 'days_since_latest_history': (day - latest).days,
              'cutoff_rule': 'Use completed games from earlier source calendar days only.'}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path('data/processed'))
    parser.add_argument('--model', type=Path, default=Path('reports/result_prediction/model.joblib'))
    parser.add_argument('--date', required=True, help='Fixture date in YYYY-MM-DD format')
    parser.add_argument('--season-start', type=int, required=True)
    parser.add_argument('--home-team-id', required=True)
    parser.add_argument('--away-team-id', required=True)
    args = parser.parse_args()
    with threadpool_limits(limits=2):
        predict(args)
