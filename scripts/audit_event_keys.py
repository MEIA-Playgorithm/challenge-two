"""Find ambiguous event identities without choosing a source version silently."""

import csv
import sqlite3
from pathlib import Path


def audit(directory):
    directory = Path(directory)
    database = directory / '_event_audit.sqlite'
    if database.exists():
        raise FileExistsError(database)
    connection = sqlite3.connect(database)
    connection.execute('CREATE TABLE keys (game TEXT, period TEXT, action TEXT, n INTEGER, '
                       'PRIMARY KEY (game, period, action)) WITHOUT ROWID')
    missing = 0
    query = ('INSERT INTO keys VALUES (?, ?, ?, 1) ON CONFLICT (game, period, action) '
             'DO UPDATE SET n=n+1')
    with (directory / 'play_by_play.csv').open(newline='') as stream:
        reader = csv.reader(stream)
        header = next(reader)
        indices = [header.index(k) for k in ('game_id', 'period', 'action_number')]
        batch = []
        for row in reader:
            key = tuple(row[i] for i in indices)
            if not all(key):
                missing += 1
                continue
            batch.append(key)
            if len(batch) == 10000:
                connection.executemany(query, batch)
                batch.clear()
        connection.executemany(query, batch)
    connection.commit()
    fields = ['game_id', 'period', 'action_number', 'source_record_count']
    conflicts = records = 0
    games = set()
    with (directory / 'event_key_conflicts.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(fields)
        for row in connection.execute('SELECT game, period, action, n FROM keys WHERE n > 1 ORDER BY game, period, action'):
            writer.writerow(row)
            conflicts += 1
            records += row[3]
            games.add(row[0])
    connection.close()
    database.unlink()
    return ({'ambiguous_keys': conflicts, 'records_with_ambiguous_key': records,
             'games_with_ambiguous_keys': len(games), 'records_missing_identity': missing},
            {'rows': conflicts, 'columns': fields, 'missing': dict.fromkeys(fields, 0)})


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.directory)[0], indent=2))
