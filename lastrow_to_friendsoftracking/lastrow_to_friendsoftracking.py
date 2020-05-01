# -*- coding: utf-8 -*-
"""
Created on Fri May  1 12:46:12 2020

@author: Ciaran Grant
"""

def lastrow_to_friendsoftracking(data):
    
    # data - dataframe in format of '../Last-Row-master/datasets/positional_data/liverpool_2019.csv'
    
    import numpy as np
    
    # Create a consistent player variable across all matches -
    # **not consistent player to player each match, but all players numbered 0-22**
    # Use player number from LastRow data to track players across matches - haven't figured that one out yet
    consistent_player_temp = []
    for match in data.index.get_level_values('play').unique():
        # get unique list of players
        players = data.loc[match]['player'].unique()

        # count number of them
        num_players = len(players)

        # create range 1:number unique players
        consistent_players = np.array(range(0,num_players))

        # map players to consistent players
        player_map = dict(zip(players, consistent_players))
        mapped_players = data.loc[match]['player'].map(player_map)
        
        # append matches together
        consistent_player_temp.extend(mapped_players)
    
    # Add to dataframe
    data['consistent_player'] = consistent_player_temp
    
    # Create attackers/defense player column - fill in missing values as the ball
    data['player_x'] = data['team'] + "_" + data['consistent_player'].map(str) + "_x"
    data['player_x'].fillna('ball_x', inplace = True)
    data['player_y'] = data['team'] + "_" + data['consistent_player'].map(str) + "_y"
    data['player_y'].fillna('ball_y', inplace = True)
    
    # Pivot long format to wide for x columns
    x_columns = [c for c in data.columns if c.lower()[-1] == 'x' or (c.lower() == 'team')]
    data_x = data[x_columns]
    data_x_reset = data_x.reset_index()
    data_x_wide = data_x_reset.pivot_table(index = ['play','frame'], columns='player_x', values='x')

    # Pivot long format to wide for y columns
    y_columns = [c for c in data.columns if c.lower()[-1] == 'y' or (c.lower() == 'team')]
    data_y = data[y_columns]
    data_y_reset = data_y.reset_index()
    data_y_wide =data_y_reset.pivot_table(index = ['play','frame'], columns='player_y', values='y')

    # Join x,y locations together
    data_wide = data_x_wide.join(data_y_wide)
    
    # Separate into Attacking/Defence to emulate Home/Away
    attack_col = [c for c in data_wide.columns if ((c.lower()[:6] == 'attack') or (c.lower()[:4] == 'ball'))]
    data_attack = data_wide[attack_col]
    defence_col = [c for c in data_wide.columns if ((c.lower()[:7] == 'defense') or (c.lower()[:4] == 'ball'))]
    data_defence = data_wide[defence_col]
    
    # Reset index to use Frame info to calculate Time [s]
    data_attack.reset_index(level='frame', inplace=True)
    data_defence.reset_index(level='frame', inplace=True)

    # 20 FPS in LastRow data
    data_attack['Time [s]'] = data_attack['frame'] / 20
    data_defence['Time [s]'] = data_defence['frame'] / 20
    
    # Add Frame back to the index
    data_attack.set_index([data_attack.index,'frame'], inplace = True)
    data_defence.set_index([data_defence.index,'frame'], inplace = True)
  
    return data_attack, data_defence
    
    

def lastrow_to_metric_coordinates(data,field_dimen=(106.,68.) ):
    
    # Adapted from @LaurieShaw's Metrics version
    
    # Get relevant columns
    x_columns = [c for c in data.columns if c[-1].lower()=='x']
    y_columns = [c for c in data.columns if c[-1].lower()=='y']
    
    # Convert to centre origin - from 0 to 100 both axis to field_dimen
    data[x_columns] = ( (data[x_columns]-50)/100 ) * field_dimen[0]
    data[y_columns] = ( (data[y_columns]-50)/100 ) * field_dimen[1] 
    
    return data

def lastrow_to_single_playing_direction(attack, defence):
    
    # Define current shooting directions
    shoot_direction = {                   
    'Liverpool [3] - 0 Bournemouth' : 'left to right', 
    'Bayern 0 - [1] Liverpool' : 'left to right',
    'Fulham 0 - [1] Liverpool' : 'right to left',
    'Southampton 1 - [2] Liverpool' : 'right to left',
    'Liverpool [2] - 0 Porto' : 'right to left',
    'Porto 0 - [2] Liverpool' : 'right to left',
    'Liverpool [4] - 0 Barcelona' : 'left to right',
    'Liverpool [1] - 0 Wolves' : 'left to right',
    'Liverpool [3] - 0 Norwich' : 'right to left',
    'Liverpool [2] - 1 Chelsea' : 'left to right',
    'Liverpool [2] - 1 Newcastle' : 'left to right',
    'Liverpool [2] - 0 Salzburg' : 'right to left',
    'Genk 0 - [3] Liverpool' : 'left to right',
    'Liverpool [2] - 0 Man City' : 'right to left',
    'Liverpool [1] - 0 Everton' : 'right to left',
    'Liverpool [2] - 0 Everton' : 'right to left',
    'Bournemouth 0 - 3 Liverpool' : 'right to left',
    'Liverpool [1] - 0 Watford' : 'right to left',
    'Leicester 0 - [3] Liverpool' : 'left to right'
    }
    
    for team in attack,defence:
        # Get relevant columns
        columns = [c for c in team.columns if c[-1].lower() in ['x','y']]
        # If match is 'left to right' then flip all x,y coordinates
        for index,row in team.iterrows():
            if shoot_direction[index[0]] == 'left to right':
                row[columns] *= -1
                
    return attack,defence