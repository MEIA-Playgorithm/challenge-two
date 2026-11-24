"""Integrate ML forecasts, constrained rotations and MDP policies across games."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from ortools.sat.python import cp_model
from threadpoolctl import threadpool_limits
from train_results import VERSION, load_history, build_features
from plan_rotation import build_roster, solve, verify_solution, plot_rotation
from plan_substitutions import SubstitutionMDP


def win_distribution(probabilities):
    distribution=np.array([1.])
    for probability in probabilities:
        if not np.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError('Probabilities must lie in [0,1]')
        distribution=np.convolve(distribution,[1-probability,probability])
    return distribution


def forecasts(games,teams,fixtures,cutoff,team_id,artifact):
    if artifact['feature_version'] != VERSION:
        raise ValueError('Result-model feature version mismatch')
    cutoff=pd.Timestamp(cutoff).normalize()
    if cutoff <= pd.Timestamp(artifact['trained_through']).normalize():
        raise ValueError('Planning cutoff must follow model training')
    history=games[pd.to_datetime(games.game_datetime_source).dt.normalize().lt(cutoff)].copy()
    history_teams=teams[teams.game_id.isin(history.game_id)].copy()
    # Only dates and team IDs from known schedules may update rest between planned games.
    schedule=games[['game_datetime_source','home_team_id','away_team_id']].copy()
    schedule['day']=pd.to_datetime(schedule.game_datetime_source).dt.normalize()
    records=[]
    for fixture in fixtures:
        day=pd.Timestamp(fixture['game_date']).normalize()
        row=build_features(history,history_teams,fixture=fixture)
        row=row[row.game_id.eq('fixture')].copy()
        for side in ['home','away']:
            tid=fixture[side+'_team_id']
            dates=schedule.loc[(schedule.home_team_id.eq(tid)|schedule.away_team_id.eq(tid)) & schedule.day.lt(day),'day']
            # Include explicitly supplied horizon fixtures, which may be absent from the source calendar.
            extra=[pd.Timestamp(f['game_date']).normalize() for f in fixtures if tid in (f['home_team_id'],f['away_team_id']) and pd.Timestamp(f['game_date']).normalize()<day]
            dates=list(dates)+extra
            if dates:
                gap=(day-max(dates)).days
                row[side+'_rest_days']=min(gap,14)
                row[side+'_back_to_back']=int(gap==1)
        home_probability=float(artifact['model'].predict_proba(row[artifact['features']])[0,1])
        probability=home_probability if fixture['home_team_id']==team_id else 1-home_probability
        records.append(dict(**fixture,win_probability=probability,
                            priority_weight=1+4*probability*(1-probability)))
    return records


def select_candidates(candidates,max_total,back_to_back_cap,time_limit=30):
    model=cp_model.CpModel()
    choices={}
    for g,options in enumerate(candidates):
        if not options:
            return {'status':'INFEASIBLE','reason':f'No feasible rotation candidates for game {g}'}
        for a,_ in enumerate(options):
            choices[g,a]=model.new_bool_var(f'choice_{g}_{a}')
        model.add(sum(choices[g,a] for a in range(len(options)))==1)
    players={p['player_id'] for options in candidates for option in options for p in option['rotation']['players']}
    minutes={(g,a,p['player_id']):p['minutes'] for g,options in enumerate(candidates)
             for a,option in enumerate(options) for p in option['rotation']['players']}
    for pid in players:
        model.add(sum(minutes.get((g,a,pid),0)*v for (g,a),v in choices.items())<=max_total)
        for g in range(1,len(candidates)):
            gap=(pd.Timestamp(candidates[g][0]['game_date'])-pd.Timestamp(candidates[g-1][0]['game_date'])).days
            if gap==1:
                model.add(sum(minutes.get((j,a,pid),0)*choices[j,a] for j in [g-1,g]
                              for a in range(len(candidates[j])))<=back_to_back_cap)
    model.maximize(sum(round(1000*candidates[g][a]['weighted_utility'])*v for (g,a),v in choices.items()))
    solver=cp_model.CpSolver()
    solver.parameters.max_time_in_seconds=time_limit
    solver.parameters.num_search_workers=1
    solver.parameters.random_seed=42
    status=solver.solve(model)
    result={'status':solver.status_name(status)}
    if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        return result
    chosen=[next(a for a in range(len(options)) if solver.value(choices[g,a])) for g,options in enumerate(candidates)]
    result.update(selected=chosen,objective=solver.objective_value/1000,best_bound=solver.best_objective_bound/1000)
    totals={pid:sum(minutes.get((g,a,pid),0) for g,a in enumerate(chosen)) for pid in sorted(players)}
    assert all(v<=max_total for v in totals.values())
    for g in range(1,len(chosen)):
        if (pd.Timestamp(candidates[g][0]['game_date'])-pd.Timestamp(candidates[g-1][0]['game_date'])).days==1:
            assert all(minutes.get((g,chosen[g],pid),0)+minutes.get((g-1,chosen[g-1],pid),0)<=back_to_back_cap for pid in players)
    result['total_minutes']=totals
    return result


def validate_fixtures(fixtures,team_id,cutoff):
    if not fixtures:
        raise ValueError('No fixtures supplied')
    dates=[]
    for f in fixtures:
        day=pd.Timestamp(f['game_date']).normalize()
        if day<pd.Timestamp(cutoff).normalize() or f['home_team_id']==f['away_team_id']:
            raise ValueError('Invalid fixture date or teams')
        if team_id not in [f['home_team_id'],f['away_team_id']]:
            raise ValueError('Every fixture must include the planned team')
        dates.append(day)
    if dates != sorted(set(dates)):
        raise ValueError('Fixtures must be chronological, with one team game per date')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,default=Path('data/processed'))
    parser.add_argument('--performance-dir',type=Path,default=Path('reports/performance'))
    parser.add_argument('--result-model',type=Path,default=Path('reports/result_prediction/model.joblib'))
    parser.add_argument('--output-dir',type=Path,default=Path('reports/horizon'))
    parser.add_argument('--team-id',default='1610612738')
    parser.add_argument('--cutoff',default='2026-04-01')
    parser.add_argument('--games',type=int,default=3)
    parser.add_argument('--target-wins',type=int,default=2)
    parser.add_argument('--max-total-minutes',type=int,default=96)
    parser.add_argument('--back-to-back-cap',type=int,default=64)
    parser.add_argument('--fixtures',type=Path,help='JSON array of dated fixtures; optional unavailable player IDs per game')
    args=parser.parse_args()
    if args.games<1 or args.max_total_minutes<0 or args.back_to_back_cap<0:
        parser.error('Game count must be positive and minute limits nonnegative')
    games,teams=load_history(args.data_dir)
    if args.fixtures:
        fixtures=json.loads(args.fixtures.read_text())
    else:
        eligible=games[(games.home_team_id.eq(args.team_id)|games.away_team_id.eq(args.team_id)) &
                       pd.to_datetime(games.game_datetime_source).dt.normalize().ge(pd.Timestamp(args.cutoff))]
        eligible=eligible.sort_values('game_datetime_source').head(args.games)
        fixtures=[dict(game_id=str(r.game_id),game_date=str(pd.Timestamp(r.game_datetime_source).date()),
                       home_team_id=str(r.home_team_id),away_team_id=str(r.away_team_id),season_start=int(r.season_start))
                  for r in eligible.itertuples()]
        if len(fixtures)!=args.games:
            raise ValueError('Not enough scheduled games; supply --fixtures')
    validate_fixtures(fixtures,args.team_id,args.cutoff)
    if not 0<=args.target_wins<=len(fixtures):
        parser.error('Target wins must lie between zero and the fixture count')
    output=args.output_dir
    output.mkdir(parents=True,exist_ok=True)
    (output/'_SUCCESS').unlink(missing_ok=True)
    artifact=joblib.load(args.result_model)
    print('Forecasting with frozen pre-cutoff results...',flush=True)
    predicted=forecasts(games,teams,fixtures,args.cutoff,args.team_id,artifact)
    print('Building pre-cutoff player priorities...',flush=True)
    # Production priorities remain fixed for the entire horizon; no future box score is used.
    roster=build_roster(args.data_dir,args.performance_dir,args.team_id,args.cutoff,home=True)
    if any(f['season_start']!=int(games.loc[pd.to_datetime(games.game_datetime_source).lt(pd.Timestamp(args.cutoff)),'season_start'].max()) for f in fixtures):
        raise ValueError('The fixed-roster horizon must stay within the latest observed season')
    candidates=[]
    for g,f in enumerate(predicted):
        options=[]
        for cap in [36,32,28]:
            config=copy.deepcopy(roster)
            config['date']=f['game_date']
            config['home']=f['home_team_id']==args.team_id
            for p in config['players']:
                p['max_minutes']=min(p['max_minutes'],cap)
                if p['player_id'] in f.get('unavailable',[]):
                    p['available']=False
            rotation=solve(config,10)
            if 'schedule' in rotation:
                options.append(dict(cap=cap,config=config,rotation=rotation,game_date=f['game_date'],
                                    weighted_utility=f['priority_weight']*rotation['objective']))
        candidates.append(options)
        print(f'Game {g+1}: {len(options)} feasible candidate rotations',flush=True)
    selection=select_candidates(candidates,args.max_total_minutes,args.back_to_back_cap)
    (output/'selection.json').write_text(json.dumps(selection,indent=2)+'\n')
    if 'selected' not in selection:
        print(json.dumps(selection)); raise SystemExit(2)
    summaries=[]
    for g,a in enumerate(selection['selected']):
        chosen=candidates[g][a]
        config,rotation=chosen['config'],chosen['rotation']
        directory=output/f'game_{g+1:02}'
        directory.mkdir(exist_ok=True)
        verify_solution(config,rotation)
        mdp=SubstitutionMDP(config,rotation)
        expected={p:mdp.expected(p) for p in ['mdp','fixed','greedy']}
        _,_,example=mdp.rollout([0]*mdp.horizon,'mdp')
        (directory/'inputs.json').write_text(json.dumps(config,indent=2)+'\n')
        (directory/'solution.json').write_text(json.dumps(rotation,indent=2)+'\n')
        states=[dict(block=s[0],remaining=list(s[1]),streak=list(s[2]),previous=s[3],context=['balanced','playmaking','rebounding'][s[4]],
                     action=action,value=mdp.value(s)) for s,action in sorted(mdp.decisions.items())]
        (directory/'policy.json').write_text(json.dumps(dict(player_order=mdp.ids,player_names={p['player_id']:p['name'] for p in mdp.players},
                                                           action_blocks=rotation['schedule'],states=states),indent=2)+'\n')
        pd.DataFrame(example['schedule']).to_csv(directory/'substitutions.csv',index=False)
        pd.DataFrame(rotation['players']).to_csv(directory/'minutes.csv',index=False)
        plot_rotation(example,directory)
        (directory/'_SUCCESS').write_text('Integrated rotation and MDP checked.\n')
        summaries.append(dict(**predicted[g],selected_cap=chosen['cap'],rotation_status=rotation['status'],
                              rotation_utility=rotation['objective'],mdp_expected_utility=expected['mdp'],
                              fixed_expected_utility=expected['fixed']))
    distribution=win_distribution([f['win_probability'] for f in predicted])
    totals=pd.DataFrame([dict(player_id=p['player_id'],name=p['name'],total_minutes=selection['total_minutes'][p['player_id']]) for p in roster['players']])
    totals.to_csv(output/'player_totals.csv',index=False)
    pd.DataFrame(summaries).to_csv(output/'games.csv',index=False)
    pd.DataFrame({'wins':range(len(distribution)),'probability':distribution}).to_csv(output/'win_distribution.csv',index=False)
    metrics=dict(team_id=args.team_id,cutoff=args.cutoff,target_wins=args.target_wins,
                 expected_wins=sum(f['win_probability'] for f in predicted),
                 probability_target=float(distribution[args.target_wins:].sum()),
                 max_total_minutes=args.max_total_minutes,back_to_back_cap=args.back_to_back_cap,
                 selection=selection,fixtures=fixtures,
                 candidate_summary=[[dict(cap=o['cap'],status=o['rotation']['status'],utility=o['rotation']['objective']) for o in options] for options in candidates],
                 model_trained_through=artifact['trained_through'],
                 result_model_sha256=hashlib.sha256(args.result_model.read_bytes()).hexdigest(),
                 source_provenance=roster['provenance'],
                 assumptions=['Independent game outcomes for win-count distribution','Frozen pre-cutoff team performance and home-context player priorities',
                              'Historical calendar treated as known at cutoff; dates and teams only','Utility is not a causal effect on win probability',
                              'Optimal only among generated candidates; not a joint global rotation optimum'])
    (output/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    lines=['# Multi-game plan','',f"Team: {args.team_id}. Planning cutoff: {args.cutoff}.",
           f"Target: {args.target_wins} wins in {len(fixtures)} games. Expected wins: {metrics['expected_wins']:.3f}.",
           f"Probability of reaching the target: {metrics['probability_target']:.1%}, assuming independent outcomes.",
           f"Candidate selection status: **{selection['status']}**.",'',
           '| Game | Date | Win probability | Selected minute cap | Plan |','| --- | --- | ---: | ---: | --- |']
    for i,s in enumerate(summaries):
        lines.append(f"| {i+1} | {s['game_date']} | {s['win_probability']:.1%} | {s['selected_cap']} | [Minutes](game_{i+1:02}/minutes.csv), [rotation](game_{i+1:02}/rotation.png) |")
    lines+=['',f'Each player is limited to {args.max_total_minutes} minutes over this horizon.',
            f'Consecutive-day games have a combined {args.back_to_back_cap}-minute limit per player.',
            'The minute limits cover listed games only. Include every team fixture in the horizon.',
            'The plan does not claim to increase these win probabilities. Rotation utility and win forecasts are separate outputs.',
            'Replan after each completed game with updated data and availability.', '',
            'See [the integration guide](../../docs/HORIZON_PLANNING.md) for assumptions, module contracts and commands.']
    (output/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    (output/'_SUCCESS').write_text('Integrated multi-game plan completed and checked.\n')
    print('\n'.join(lines))

if __name__=='__main__':
    with threadpool_limits(limits=2):
        main()
