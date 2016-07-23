from __future__ import division
import json
import sys
import init

def calc_team_record_ranking(team):
    for opp in team['opponents']:
        team['opponent_games'] += teams[opp]['games']
        team['opponent_wins'] += teams[opp]['wins']

    for opp in team['game_win_opponents']:
        team['game_win_opponents_games'] += teams[opp]['games']
        team['game_win_opponents_wins'] += teams[opp]['wins']

    team['points_scored_avg'] = team['points_scored'] / team['games']
    team['points_against_avg'] = team['points_against'] / team['games']
    team['point_differential_avg'] = team['point_differential'] / team['games']

    if team['opponent_wins'] > 0:
        team['sos'] = team['opponent_wins'] / team['opponent_games']
    else:
        team['sos'] = 0

    if team['game_win_opponents_wins']:
        team['sov'] = team['game_win_opponents_wins'] / team['game_win_opponents_games']
    else:
        team['sov'] = 0

    team['win_percentage'] = team['wins'] / team['games']

def calc_value_ranking(teams, valueKey, rankingKey, reverse):
    prevAvg = None
    index = 32
    indexSeries = 0

    for id, team in sorted(teams.iteritems(), key=lambda (x, y): y[valueKey], reverse=reverse):
        if prevAvg == team[valueKey]:
            indexSeries += 1
        elif indexSeries > 0:
            indexSeries = 0

        prevAvg = team[valueKey]
        team[rankingKey] = index + indexSeries
        index -= 1

def calc_value_transformation(teams, valueKey, transformationKey, reverse):
    index = 0
    transformationValue = 10

    for id, team in sorted(teams.iteritems(), key=lambda (x, y): y[valueKey], reverse=reverse):
        if index == 0:
            baselineAvg = team[valueKey]
            team[transformationKey] = transformationValue
        else:
            if reverse == True:
                team[transformationKey] = (team[valueKey] / baselineAvg) * transformationValue
            else:
                team[transformationKey] = (baselineAvg / team[valueKey]) * transformationValue

        index += 1

def calc_power_ranking(team):
    team['win_value'] = (team['wins'] * team['sov']) * 0.50
    team['point_differential_value'] = (team['point_differential_avg'] * team['sos']) * 0.25
    team['points_scored_value'] = team['points_scored_transformation'] * 0.10
    team['points_against_value'] = team['points_against_transformation'] * 0.10
    team['turnover_differential_value'] = team['turnover_differential_transformation'] * 0.05

    team['power_ranking'] = team['win_value'] + team['point_differential_value'] + team['points_scored_value'] + team['points_against_value'] + team['turnover_differential_value']

def print_power_rankings(teams):
    index = 1

    for id, team in sorted(teams.iteritems(), key=lambda (x, y): y['power_ranking'], reverse=True):
        print '%d. %s %d-%d %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f' % (index, team['id'], team['wins'], team['losses'], team['power_ranking'], team['sos'], team['sov'], team['win_value'], team['point_differential_value'], team['points_scored_value'], team['points_against_value'], team['turnover_differential_value'])
        index += 1

def export_to_json(teams):
    data = {}
    rankings = []
    name = str(input_year) + '_wk_' + str(input_week)
    fileName = name + '.json'

    for id, team in sorted(teams.iteritems(), key=lambda (x, y): y['power_ranking'], reverse=True):
        rankings.append(team)

    data['_id'] = name
    data['data'] = rankings

    with open(fileName, 'w') as outfile:
        json.dump(data, outfile)

global teams
global input_year
global input_week

input_year = int(sys.argv[1])
input_week = int(sys.argv[2])

teams = init.init_teams(input_year, input_week);

for id, team in teams.iteritems():
    calc_team_record_ranking(team)

calc_value_ranking(teams, 'points_scored_avg', 'points_scored_ranking', True)
calc_value_ranking(teams, 'points_against_avg', 'points_against_ranking', False)
calc_value_ranking(teams, 'turnover_differential', 'turnover_differential_ranking', True)
calc_value_transformation(teams, 'points_scored_avg', 'points_scored_transformation', True)
calc_value_transformation(teams, 'points_against_avg', 'points_against_transformation', False)
calc_value_transformation(teams, 'turnover_differential', 'turnover_differential_transformation', True)

for id, team in teams.iteritems():
    calc_power_ranking(team)

print_power_rankings(teams)
export_to_json(teams)
