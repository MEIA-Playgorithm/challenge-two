#!/usr/bin/env python3
"""Build the shared NBA datasets using Python's standard library only."""

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_event_keys import audit as audit_event_keys


PRIMARY = 'kaggle_eoinamoore_historical_nba'
ALIASES = {
    'gameId': 'game_id', 'personId': 'player_id', 'teamId': 'team_id',
    'playerteamId': 'team_id', 'opponentteamId': 'opponent_team_id',
    'opponentTeamId': 'opponent_team_id', 'hometeamId': 'home_team_id',
    'awayteamId': 'away_team_id', 'gameDateTimeEst': 'game_datetime_source',
    'numMinutes': 'minutes', 'person_id': 'player_id',
}
EVENT_COLUMNS = [
    'gameId', 'actionNumber', 'actionId', 'orderNumber', 'period', 'clock',
    'actionType', 'subType', 'description', 'teamId', 'personId',
    'subsInPersonId', 'scoreHome', 'scoreAway', 'possession', 'timeActual',
    'x', 'y', 'shotResult', 'shotValue', 'isFieldGoal', 'personIdsFilter',
]


@lru_cache(maxsize=1024)
def snake(name):
    return ALIASES.get(name, re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower())


def identifier(value, game=False):
    value = str(value or '').strip()
    if not value:
        return ''
    if re.fullmatch(r'\d+\.0+', value):
        value = value.split('.')[0]
    if not value.isdigit():
        raise ValueError('invalid identifier: ' + value)
    value = str(int(value))
    if game and len(value) > 10:
        raise ValueError('game identifier exceeds 10 digits')
    return value.zfill(10) if game else value


def number(value):
    if value == '' or value is None:
        return None
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('non-finite number')
    return result


def minutes(value):
    if ':' in value:
        m, s = value.split(':')
        if number(m) < 0 or not 0 <= number(s) < 60:
            raise ValueError('invalid seconds')
        return str(float(m) + float(s) / 60)
    if value and number(value) < 0:
        raise ValueError('negative minutes')
    return value


def normalize(row):
    out = {}
    for key, value in row.items():
        key = snake(key)
        value = (value or '').strip()
        if key.endswith('_id') and key not in {'action_id', 'arena_id'}:
            value = identifier(value, key == 'game_id')
        if key == 'minutes':
            value = minutes(value)
        out[key] = value
    return out


def season_from_id(game_id):
    """NBA game IDs encode season start, including delayed 2019/2020 games."""
    year = int(game_id[3:5])
    return 2000 + year if year < 46 else 1900 + year


class Table:
    def __init__(self, path, fields):
        self.path, self.fields = path, fields
        self.file = path.open('w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames=fields, extrasaction='raise')
        self.writer.writeheader()
        self.rows = 0
        self.missing = Counter()

    def add(self, row):
        self.writer.writerow(row)
        self.rows += 1
        self.missing.update(k for k in self.fields if row.get(k, '') in ('', None))

    def close(self):
        self.file.close()
        return {'rows': self.rows, 'columns': self.fields,
                'missing': {k: self.missing[k] for k in self.fields}}


class Pipeline:
    def __init__(self, args):
        self.args = args
        self.root, self.out = args.input, args.output
        # A new directory prevents stale tables from looking like current results.
        self.out.mkdir(parents=True, exist_ok=False)
        self.tables = {}
        self.report = {'scope': {'start_season': args.start_season,
                                'end_season': args.end_season,
                                'game_type': 'Regular season: 002 IDs, including NBA Cup games'},
                       'inputs': {}, 'tables': {}, 'checks': {}, 'warnings': []}
        self.games = {}
        self.player_ids = set()
        self.team_keys = set()
        self.player_keys = set()
        self.rejects = self.table('quarantine', ['source_file', 'source_row', 'reason', 'record_json'])
        self.repairs = self.table('repairs', ['source_file', 'source_row', 'game_id', 'player_id', 'field', 'value', 'rule'])

    def table(self, name, fields):
        table = Table(self.out / (name + '.csv'), fields)
        self.tables[name] = table
        return table

    def read(self, relative, game_column=None, selected=None):
        path = self.root / relative
        meta = self.report['inputs'].setdefault(str(relative), {})
        count = 0
        with path.open(newline='', encoding='utf-8-sig') as stream:
            reader = csv.reader(stream)
            fields = next(reader)
            index = fields.index(game_column) if game_column else None
            for line, values in enumerate(reader, 2):
                count += 1
                if count % 1_000_000 == 0:
                    print(f'  {relative}: {count:,} source rows scanned', flush=True)
                if len(values) != len(fields):
                    self.reject(relative, line, 'wrong_column_count', {'values': values})
                    continue
                if index is not None and selected is not None:
                    try:
                        key = identifier(values[index], True)
                    except ValueError:
                        self.reject(relative, line, 'invalid_game_id', dict(zip(fields, values)))
                        continue
                    if key not in selected:
                        continue
                yield line, dict(zip(fields, values))
        meta['rows_scanned'] = count

    def reject(self, source, line, reason, row):
        self.rejects.add({'source_file': str(source), 'source_row': line,
                          'reason': reason, 'record_json': json.dumps(row, ensure_ascii=False)})

    def inventory(self):
        for path in sorted(self.root.rglob('*.csv')):
            with path.open(newline='', encoding='utf-8-sig') as stream:
                fields = next(csv.reader(stream))
            self.report['inputs'][str(path.relative_to(self.root))] = {
                'bytes': path.stat().st_size, 'columns': fields,
                'mtime_ns': path.stat().st_mtime_ns,
            }

    def prepare_games(self):
        path = Path(PRIMARY) / 'Games.csv'
        fields = [snake(c) for c in self.report['inputs'][str(path)]['columns']]
        table = self.table('games', fields + ['season_start', 'home_win', 'split'])
        seasons = Counter()
        for line, raw in self.read(path):
            if (raw['gameType'] != 'Regular Season' and
                    not raw['gameId'].split('.')[0].zfill(10).startswith('002')):
                continue
            try:
                row = normalize(raw)
                gid = row['game_id']
                if not gid or gid[:3] != '002':
                    raise ValueError('regular season label conflicts with game ID prefix')
                season = season_from_id(gid)
                if not self.args.start_season <= season <= self.args.end_season:
                    continue
                date = datetime.fromisoformat(row['game_datetime_source'])
                if date.year not in (season, season + 1):
                    raise ValueError('date outside season years')
                home, away = number(row['home_score']), number(row['away_score'])
                if home is None or away is None or min(home, away) <= 0 or home == away:
                    raise ValueError('missing or invalid final score')
                if not home.is_integer() or not away.is_integer():
                    raise ValueError('non-integer score')
                if not row['home_team_id'] or not row['away_team_id'] or row['home_team_id'] == row['away_team_id']:
                    raise ValueError('invalid opposing teams')
                winner = row['home_team_id'] if home > away else row['away_team_id']
                if row['winner'] and identifier(row['winner']) != winner:
                    raise ValueError('winner disagrees with score')
                if gid in self.games:
                    raise ValueError('duplicate game key')
                row.update(season_start=season, home_win=int(home > away),
                           split='test' if season == self.args.end_season else
                           'validation' if season == self.args.end_season - 1 else 'train')
                self.games[gid] = row
                table.add(row)
                seasons[season] += 1
            except (ValueError, TypeError) as error:
                self.reject(path, line, str(error), raw)
        if not self.games:
            raise ValueError('No games in requested scope')
        self.report['checks']['games_by_season'] = dict(sorted(seasons.items()))

    def prepare_stats(self, filename, name, player=False, extended=False):
        path = Path(PRIMARY) / filename
        fields = [snake(c) for c in self.report['inputs'][str(path)]['columns']]
        table = self.table(name, fields + ['season_start'] + (['participation_status'] if player else []))
        seen = set()
        for line, raw in self.read(path, 'gameId', self.games):
            try:
                row = normalize(raw)
                gid = row['game_id']
                game = self.games[gid]
                repaired = []
                if player and (not row['team_id'] or not row['opponent_team_id']):
                    # Only repair IDs when the home flag AND both team names agree.
                    side = 'hometeam' if row.get('home') == '1' else 'awayteam' if row.get('home') == '0' else None
                    other_side = 'awayteam' if side == 'hometeam' else 'hometeam'
                    if side and all(row.get(prefix + '_' + suffix) and
                                    row[prefix + '_' + suffix].casefold() == game[game_prefix + '_' + suffix].casefold()
                                    for prefix, game_prefix in [('playerteam', side), ('opponentteam', other_side)]
                                    for suffix in ('city', 'name')):
                        for col, value in [('team_id', game['home_team_id'] if side == 'hometeam' else game['away_team_id']),
                                           ('opponent_team_id', game['away_team_id'] if side == 'hometeam' else game['home_team_id'])]:
                            if not row[col]:
                                row[col] = value
                                repaired.append((col, value))
                tid = row['team_id']
                if tid not in (game['home_team_id'], game['away_team_id']):
                    raise ValueError('team not in game')
                other = game['away_team_id'] if tid == game['home_team_id'] else game['home_team_id']
                if row['opponent_team_id'] != other:
                    raise ValueError('opponent not in game')
                if row.get('home', '') not in ('', str(int(tid == game['home_team_id']))):
                    raise ValueError('home flag mismatch')
                key = (gid, row['player_id']) if player else (gid, tid)
                if player and not row['player_id']:
                    raise ValueError('missing player ID')
                if key in seen:
                    raise ValueError('duplicate business key')
                if extended and key not in (self.player_keys if player else self.team_keys):
                    raise ValueError('no accepted basic statistics row')
                if not player:
                    expected = game['home_score'] if tid == game['home_team_id'] else game['away_score']
                    if number(row['team_score']) != number(expected):
                        raise ValueError('team score mismatch')
                for made, attempted in [('field_goals_made', 'field_goals_attempted'),
                                        ('three_pointers_made', 'three_pointers_attempted'),
                                        ('free_throws_made', 'free_throws_attempted')]:
                    a, b = number(row.get(made)), number(row.get(attempted))
                    if a is not None and b is not None and not 0 <= a <= b:
                        raise ValueError('invalid made/attempted counts')
                row['season_start'] = game['season_start']
                if player:
                    played_minutes = number(row['minutes'])
                    row['participation_status'] = ('unknown' if played_minutes is None else
                                                   'played' if played_minutes > 0 else 'zero_minutes')
                table.add(row)
                for col, value in repaired:
                    self.repairs.add({'source_file': str(path), 'source_row': line, 'game_id': gid,
                                      'player_id': row['player_id'], 'field': col, 'value': value,
                                      'rule': 'home flag and both city/name pairs match game'})
                seen.add(key)
                if player:
                    self.player_ids.add(row['player_id'])
            except (ValueError, TypeError) as error:
                self.reject(path, line, str(error), raw)
        if not extended:
            if player:
                self.player_keys = seen
            else:
                self.team_keys = seen
        self.report['checks'][name + '_games_covered'] = len({k[0] for k in seen})
        if not player:
            self.report['checks'][name + '_missing_team_rows'] = len(self.games) * 2 - len(seen)
        if extended:
            base = self.player_keys if player else self.team_keys
            self.report['checks'][name + '_missing_basic_keys'] = len(base - seen)

    def prepare_players(self):
        path = Path(PRIMARY) / 'Players.csv'
        fields = [snake(c) for c in self.report['inputs'][str(path)]['columns']]
        table = self.table('players', fields + ['height_cm', 'weight_kg'])
        seen = set()
        for line, raw in self.read(path):
            try:
                row = normalize(raw)
                pid = row['player_id']
                if pid not in self.player_ids:
                    continue
                if pid in seen:
                    raise ValueError('duplicate player key')
                row['height_cm'] = round(number(row['height_inches']) * 2.54, 3) if row['height_inches'] else ''
                row['weight_kg'] = round(number(row['body_weight_lbs']) * 0.45359237, 3) if row['body_weight_lbs'] else ''
                table.add(row)
                seen.add(pid)
            except (ValueError, TypeError) as error:
                self.reject(path, line, str(error), raw)
        missing = sorted(self.player_ids - seen)
        self.report['checks']['players_missing_biography'] = missing
        # Keep the dimension join complete without inventing personal details.
        for pid in missing:
            table.add({'player_id': pid})

    def cross_source(self):
        audit = self.table('source_game_matches', ['source', 'game_id', 'date_match', 'teams_match', 'scores_match'])
        specs = [
            ('kaggle_wyattowalsh_basketball/game.csv', 'game_id', 'game_date',
             'team_id_home', 'team_id_away', 'pts_home', 'pts_away'),
            ('kaggle_nathanlauga_nba_games/games.csv', 'GAME_ID', 'GAME_DATE_EST',
             'HOME_TEAM_ID', 'VISITOR_TEAM_ID', 'PTS_home', 'PTS_away'),
        ]
        for source, gidcol, datecol, homecol, awaycol, hscol, ascol in specs:
            counts = Counter()
            for line, row in self.read(source, gidcol, self.games):
                try:
                    gid = identifier(row[gidcol], True)
                    game = self.games[gid]
                    checks = {
                        'date_match': row[datecol][:10] == game['game_datetime_source'][:10],
                        'teams_match': (identifier(row[homecol]), identifier(row[awaycol])) ==
                                      (game['home_team_id'], game['away_team_id']),
                        'scores_match': (number(row[hscol]), number(row[ascol])) ==
                                       (number(game['home_score']), number(game['away_score'])),
                    }
                    audit.add({'source': source, 'game_id': gid, **{k: int(v) for k, v in checks.items()}})
                    counts['overlapping_rows'] += 1
                    counts.update(k + '_mismatch' for k, v in checks.items() if not v)
                except ValueError as error:
                    self.reject(source, line, str(error), row)
            self.report['checks'][source] = dict(counts)
        path = 'kaggle_wyattowalsh_basketball/common_player_info.csv'
        primary_names = {}
        self.tables['players'].file.flush()
        with (self.out / 'players.csv').open() as stream:
            for row in csv.DictReader(stream):
                primary_names[row['player_id']] = (row['first_name'] + ' ' + row['last_name']).strip()
        table = self.table('source_player_matches', ['player_id', 'primary_name', 'secondary_name', 'name_match'])
        for line, row in self.read(path):
            try:
                pid = identifier(row['person_id'])
                if pid in primary_names:
                    name = row['display_first_last'].strip()
                    table.add({'player_id': pid, 'primary_name': primary_names[pid],
                               'secondary_name': name,
                               'name_match': int(primary_names[pid].casefold() == name.casefold())})
            except ValueError as error:
                self.reject(path, line, str(error), row)

    def prepare_injuries(self):
        paths = sorted((self.root / 'sportsdataverse_injuries').glob('injury_report_*.csv'))
        fields = [snake(c) for c in self.report['inputs'][str(paths[0].relative_to(self.root))]['columns']]
        table = self.table('injury_reports', fields + ['source_file', 'source_row'])
        seen = set()
        coverage = set()
        counts = Counter()
        for full in paths:
            path = full.relative_to(self.root)
            for line, raw in self.read(path, 'game_id', self.games):
                try:
                    row = normalize(raw)
                    gid, tid, pid = row['game_id'], row['team_id'], row['player_id']
                    game = self.games[gid]
                    if tid not in (game['home_team_id'], game['away_team_id']):
                        raise ValueError('injury team not in game')
                    if row['game_date'][:10] != game['game_datetime_source'][:10]:
                        raise ValueError('injury game date mismatch')
                    datetime.fromisoformat(row['report_datetime'])
                    # Repeated publications are distinct observations, not duplicates.
                    key = tuple(row.get(k, '') for k in fields)
                    if key in seen:
                        counts['exact_duplicates_removed'] += 1
                        continue
                    seen.add(key)
                    if not pid:
                        counts['missing_player_id'] += 1
                    elif pid not in self.player_ids:
                        counts['player_not_in_selected_boxscores'] += 1
                    row.update(source_file=str(path), source_row=line)
                    table.add(row)
                    coverage.add(gid)
                except (ValueError, TypeError) as error:
                    self.reject(path, line, str(error), raw)
        self.report['checks']['injuries'] = {**counts, 'games_covered': len(coverage)}
        self.report['warnings'].append(
            'Injury reports retain all publication times. Source timezone semantics are unverified. '
            'No pregame availability snapshot is supplied; confirm timezones and apply an as-of cutoff before prediction.')

    def prepare_events(self):
        path = Path(PRIMARY) / 'PlayByPlay.csv'
        fields = [snake(c) for c in EVENT_COLUMNS]
        table = self.table('play_by_play', fields + ['source_row', 'clock_seconds_remaining'])
        fingerprints = set()
        coverage, actions = Counter(), Counter()
        duplicates = 0
        for line, raw in self.read(path, 'gameId', self.games):
            try:
                row = normalize({k: raw[k] for k in EVENT_COLUMNS})
                gid = row['game_id']
                if row['team_id'] and row['team_id'] != '0' and row['team_id'] not in (
                        self.games[gid]['home_team_id'], self.games[gid]['away_team_id']):
                    raise ValueError('event team not in game')
                # Hash the full source record, not the reduced output or action number.
                digest = hashlib.sha256(json.dumps(list(raw.values()), separators=(',', ':')).encode()).digest()
                if digest in fingerprints:
                    duplicates += 1
                    continue
                fingerprints.add(digest)
                clock = row['clock']
                match = re.fullmatch(r'PT(\d+)M([\d.]+)S', clock)
                if match:
                    remaining = int(match[1]) * 60 + float(match[2])
                elif re.fullmatch(r'\d+:\d+(?:\.\d+)?', clock):
                    m, s = clock.split(':')
                    remaining = int(m) * 60 + float(s)
                elif not clock:
                    remaining = ''
                else:
                    raise ValueError('unrecognized event clock')
                row.update(source_row=line, clock_seconds_remaining=remaining)
                table.add(row)
                coverage[gid] += 1
                actions[row['action_type']] += 1
            except (ValueError, TypeError) as error:
                self.reject(path, line, str(error), raw)
        table = self.table('event_coverage', ['game_id', 'event_count'])
        for gid in sorted(self.games):
            table.add({'game_id': gid, 'event_count': coverage[gid]})
        self.report['checks']['play_by_play'] = {
            'games_covered': len(coverage), 'games_without_events': len(self.games) - len(coverage),
            'exact_duplicates_removed': duplicates, 'action_types': dict(actions),
        }
        self.report['warnings'].append(
            'Events are prepared, but five-player lineups are not reconstructed or certified. '
            'Source row preserves order; action numbers are not assumed unique. '
            'Check starters, substitutions, periods and event coverage before lineup analysis.')

    def finish(self):
        for relative, meta in self.report['inputs'].items():
            if 'rows_scanned' in meta:
                path = self.root / relative
                if path.stat().st_mtime_ns != meta['mtime_ns']:
                    raise RuntimeError('Input changed during preparation: ' + relative)
                with path.open('rb') as stream:
                    meta['sha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
        for name, table in self.tables.items():
            self.report['tables'][name] = table.close()
        self.report['warnings'].extend([
            'Game timestamps retain the source value without an assumed timezone.',
            'Season coverage describes observed rows, not independently certified complete seasons.',
            'Basic and extended statistics remain separate. Join on documented keys with cardinality validation.',
            'Box scores and season totals contain postgame information. Shift histories before predicting games.',
            'Player biographies are source snapshots. Height, weight and career fields are not historical measurements.',
            'Missing values remain empty. Fit any imputation or scaling on training data only.',
        ])
        reasons = Counter()
        with (self.out / 'quarantine.csv').open() as stream:
            for row in csv.DictReader(stream):
                reasons[row['reason']] += 1
        self.report['checks']['quarantine_reasons'] = dict(reasons)
        self.report['created_at_utc'] = datetime.now(timezone.utc).isoformat()
        self.report['command_scope'] = vars(self.args).copy()
        self.report['command_scope'] = {k: str(v) if isinstance(v, Path) else v
                                        for k, v in self.report['command_scope'].items()}
        (self.out / 'quality_report.json').write_text(json.dumps(self.report, indent=2) + '\n')
        with (self.out / 'data_dictionary.csv').open('w', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['table', 'column', 'storage', 'missing_values', 'note'])
            for name, table in self.report['tables'].items():
                for col in table['columns']:
                    note = 'Normalized source column; see input manifest and preparation guide.'
                    if col.endswith('_id'):
                        note = 'Read as string. Game IDs have 10 digits; preserve leading zeros.'
                    elif col == 'minutes':
                        note = 'Decimal minutes; empty is unknown, zero is preserved.'
                    elif col == 'season_start':
                        note = 'Season start year decoded from NBA game ID.'
                    elif col == 'split':
                        note = 'Chronological: final season test, preceding season validation, earlier seasons train.'
                    elif col == 'home_win':
                        note = 'Postgame target: 1 if home score exceeds away score, otherwise 0.'
                    elif col == 'clock_seconds_remaining':
                        note = 'Seconds remaining in the event period, parsed from source clock.'
                    writer.writerow([name, col, 'CSV text', table['missing'][col], note])
        lines = ['# Data quality report', '',
                 'Generated by `scripts/prepare_data.py`. See `quality_report.json` for full checks.', '',
                 '| Table | Rows |', '| --- | ---: |']
        lines += [f'| {name} | {meta["rows"]:,} |' for name, meta in self.report['tables'].items()]
        lines += ['', '## Checks', '', '```json', json.dumps(self.report['checks'], indent=2), '```',
                  '', '## Limitations', '']
        lines += ['- ' + warning for warning in self.report['warnings']]
        (self.out / 'QUALITY_REPORT.md').write_text('\n'.join(lines) + '\n')
        (self.out / '_SUCCESS').write_text('Preparation completed. Review quality_report.json before modeling.\n')

    def audit_events(self):
        self.tables['play_by_play'].file.flush()
        checks, profile = audit_event_keys(self.out)
        self.report['checks']['event_identity'] = checks
        self.report['tables']['event_key_conflicts'] = profile
        self.report['warnings'].append(
            'event_key_conflicts.csv lists repeated game/period/action-number identities. '
            'Resolve source versions before counting events or reconstructing lineups; no arbitrary version is selected.')

    def run(self):
        steps = [('Inventory', self.inventory), ('Games', self.prepare_games)]
        for filename, name, player, extended in [
            ('TeamStatistics.csv', 'team_games', False, False),
            ('PlayerStatistics.csv', 'player_games', True, False),
            ('TeamStatisticsExtended.csv', 'team_games_extended', False, True),
            ('PlayerStatisticsExtended.csv', 'player_games_extended', True, True),
        ]:
            steps.append((name, lambda f=filename, n=name, p=player, e=extended:
                          self.prepare_stats(f, n, p, e)))
        steps += [('Players', self.prepare_players), ('Cross-source checks', self.cross_source),
                  ('Injuries', self.prepare_injuries), ('Play-by-play', self.prepare_events),
                  ('Event identity audit', self.audit_events), ('Reports', self.finish)]
        try:
            for name, action in steps:
                print(name + '...', flush=True)
                action()
        finally:
            for table in self.tables.values():
                if not table.file.closed:
                    table.file.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=Path('data/csv'))
    parser.add_argument('--output', type=Path, default=Path('data/processed'))
    parser.add_argument('--start-season', type=int, default=2019)
    parser.add_argument('--end-season', type=int, default=2025)
    args = parser.parse_args()
    if not 1946 <= args.start_season <= args.end_season <= 2045:
        parser.error('Use season start years between 1946 and 2045, in ascending order.')
    if args.end_season - args.start_season < 2:
        parser.error('Select at least three seasons for train, validation and test.')
    Pipeline(args).run()


if __name__ == '__main__':
    main()
