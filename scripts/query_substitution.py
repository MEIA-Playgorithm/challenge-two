"""Look up an exported MDP decision for an observed discrete state."""
import argparse
import json
from pathlib import Path
from plan_rotation import ROLES


def lookup(policy, state):
    keys=('block','remaining','streak','previous','context')
    for row in policy['states']:
        if all(row[k]==state[k] for k in keys):
            action=row['action']
            assignment={r:policy['action_blocks'][action][r] for r in ROLES}
            current=set() if state['previous']==-1 else {policy['action_blocks'][state['previous']][r] for r in ROLES}
            chosen=set(assignment.values())
            names=policy['player_names']
            return dict(source_block=action,assignment=assignment,
                        entering=[dict(player_id=p,name=names[p]) for p in sorted(chosen-current)],
                        leaving=[dict(player_id=p,name=names[p]) for p in sorted(current-chosen)],
                        expected_remaining_utility=row['value'])
    raise ValueError('State is absent from this policy; recompute for changed constraints or a different trajectory')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy',type=Path,default=Path('reports/substitutions/policy.json'))
    parser.add_argument('--state',type=Path,help='JSON with block, remaining, streak, previous and context; defaults to initial state')
    args=parser.parse_args()
    policy=json.loads(args.policy.read_text())
    state=json.loads(args.state.read_text()) if args.state else next(r for r in policy['states'] if r['block']==0 and r['context']=='balanced')
    try:
        result=lookup(policy,state)
    except (ValueError,KeyError) as exc:
        parser.error(str(exc))
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
