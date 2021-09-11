from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
import requests
import  pandas as pd


def get_player_stats(year:int=2021) -> pd.DataFrame:
    """Retrieves the year by year player stats from 
       https://afltables.com/afl/stats/

    Args:
        year (int, optional): Year to retrieve stats from. Defaults to 2021.
    
    Raises:
        HTTPError: 
        Exception

    Returns:
        pd.DataFramet: A data frame with player names ad the index and statistics as the column names
    """
    try:
        r = requests.get(f'https://afltables.com/afl/stats/{year}.html')
    except HTTPError as http_err:
        print(f'HTTP Error: {http_err}')
    except Exception as e:
        print(f'Exception: {e}')
    else:
        print('Loading Data:')
    
    html_content = BeautifulSoup(r.content, features="html.parser")

    # Extract the statistics headers from the first table
    table_header =  html_content.find_all('span') 
    stats_keys = [a.split('=')[1].lower().replace(' ', '_') for a in table_header[1].stripped_strings]
    stats_keys.insert(1, 'player')

    
    players = {}    
    for row in html_content.find_all('tr'): # Iterate over table rows
        player_stats = {stats_keys[i]:data.string for i, data in enumerate(row.find_all('td'))}
        if player_stats and player_stats.get('player') is not None:
            players[player_stats['player']] = {key:(value if value != '\xa0' else 'NA')
             for key, value in player_stats.items() if key != 'player'}              

    return pd.DataFrame.from_dict(players, orient='index')

    
    



    




if __name__ == '__main__':
    main()