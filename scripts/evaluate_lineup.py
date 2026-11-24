"""Score two supplied starting quintets using the fitted Element 3 model."""
import argparse
import json
from pathlib import Path

import joblib

from train_performance import lineup_features


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', nargs=5, required=True, metavar='PLAYER_ID')
    parser.add_argument('--away', nargs=5, required=True, metavar='PLAYER_ID')
    parser.add_argument('--model', type=Path, default=Path('reports/performance/lineup_model.joblib'))
    args = parser.parse_args()
    if len(set(args.home+args.away)) != 10:
        parser.error('Supply ten distinct player IDs')
    bundle = joblib.load(args.model)
    features = lineup_features(args.home, args.away, bundle['include_quintet'])
    vectorizer = bundle['vectorizer']
    unknown = [p for p in args.home+args.away if 'player:'+p not in vectorizer.vocabulary_]
    prediction = bundle['baseline'] if bundle['model'] is None else float(
        bundle['model'].predict(vectorizer.transform([features]))[0])
    print(json.dumps({'predicted_home_game_margin': prediction, 'unknown_players': unknown,
                      'model': bundle['selected'],
                      'scope': 'Starting-lineup association with full-game margin; not causal or on-court net rating'}, indent=2))


if __name__ == '__main__':
    main()
