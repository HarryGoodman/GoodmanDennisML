from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
import requests
import pandas as pd
import numpy as np
from typing import List
import logging
import os


def get_player_stats(year: int = 2021) -> pd.DataFrame:
    """Retrieves the year by year player stats from
       https://afltables.com/afl/stats/

    Args:
        year (int, optional): Year to retrieve stats from. Acceptable range (1897-2021).
         Defaults to 2021.

    Raises:
        HTTPError:
        Exception

    Returns:
        pd.DataFramet: A data frame with player names as the index and statistics as the column names.

    """
    if not (1987 <= year <= 2021):
        raise ValueError(f"{year=} is not in range: 1897-2021")

    logging.basicConfig(
        filename=os.path.join("AFL", "data", "logs", f"afl_stats_year_data_{year}.log"),
        filemode="w",
        level=logging.DEBUG,
        format="%(asctime)s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    try:
        r = requests.get(f"https://afltables.com/afl/stats/{year}.html")
    except HTTPError as http_err:
        print(f"HTTP Error: {http_err}")
    except Exception as e:
        print(f"Exception: {e}")
    else:
        print("Loading Data:")

    logging.info(f"Accessing data for {year}")

    html_content = BeautifulSoup(r.content, features="html.parser")

    stats_keys = parse_table_headers(html_content, player_index=1)

    players = {}
    for row in html_content.find_all("tr"):
        player_stats = {
            stats_keys[i]: data.string for i, data in enumerate(row.find_all("td"))
        }
        if player_stats and player_stats.get("player") is not None:
            players[player_stats["player"]] = {
                key: (value if value != "\xa0" else "NA")
                for key, value in player_stats.items()
                if key != "player"
            }

    logging.debug(f"Players : {players.keys()}")

    return pd.DataFrame.from_dict(players, orient="index")


def parse_table_headers(html_content, player_index: int = 1) -> List[str]:
    """Parses the table headers

    Args:
        html_content ([type]): html content
        player_index (int, optional): Index which to insert  the player name as a column header. Defaults to 1.

    Returns:
        List[str]: List of parsed table headers
    """
    table_header = html_content.find_all("span")
    parsed_table_headers = [
        a.split("=")[1].lower().replace(" ", "_")
        for a in table_header[1].stripped_strings
    ]
    parsed_table_headers.insert(player_index, "player")

    return parsed_table_headers


def get_game_by_game_stats(year: int = 2021) -> pd.DataFrame:
    """Retrieves the detailed game by game afl statistics for a year
       between 1965 and 2021 available from
       https://afltables.com/afl/stats/teams/{team}/{year}_gbg.html

    Args:
        year (int, optional): Year to retrieve stats from. Acceptable range (1965-2021).
                                Defaults to 2021.

    Raises:
        ValueError: if year is outside the range 1965-2021

    Returns:
        pd.DataFrame: A pandas data frame which  has columns array([player, team, round, opponent, statistic, value])
    """

    if not (1965 <= year <= 2021):
        raise ValueError(f"{year=} is not in range: 1965-2021")

    logging.basicConfig(
        filename=os.path.join(
            "AFL", "data", "logs", f"afl_stats_game_by_game_data_{year}.log"
        ),
        filemode="w",
        level=logging.DEBUG,
        format="%(asctime)s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )

    teams = [
        "adelaide",
        "brisbaneb",
        "brisbanel",
        "carlton",
        "collingwood",
        "essendon",
        "fitzroy",
        "fremantle",
        "geelong",
        "goldcoast",
        "gws",
        "hawthorn",
        "melbourne",
        "kangaroos",
        "padelaide",
        "richmond",
        "stkilda",
        "swans",
        "westcoast",
        "bullldogs",
    ]
    ## REMOVE

    URL = "https://afltables.com/afl/stats/teams/"
    url_func = lambda team: f"{URL}{team}/{year}_gbg.html"
    gbg_content = {}
    for team in teams:
        r = requests.get(url_func(team))
        if r.status_code != 200:
            continue
        html_content = BeautifulSoup(r.content, features="html.parser")
        opponents = [
            s.string
            for s in html_content.find("tfoot").find_all("tr")[1].find_all("th")
        ]
        opponents = opponents[1:-1]
        for body, header in zip(
            html_content.find_all("tbody"), html_content.find_all("thead")
        ):
            table_name = header.find("tr").find("th").string
            table_name = table_name.lower().replace(" ", "_")
            for table_row in body.find_all("tr"):
                table_content = [
                    s.string.replace("\xa0", "NA").replace("-", "NA")
                    for s in table_row.find_all("td")
                ]
                # table_content = [int(i) if i != 'NA' else np.np.NaN for idx, i in enumerate(table_content[:-1])]

                if table_content[0] not in gbg_content.keys():
                    gbg_content[table_content[0]] = {table_name: table_content[1:-1]}
                    gbg_content[table_content[0]]["opponents"] = opponents
                    gbg_content[table_content[0]]["team"] = [
                        team for _ in range(len(opponents))
                    ]
                else:
                    gbg_content[table_content[0]][table_name] = table_content[1:-1]
    # Turn into pandas
    for key, values in gbg_content.items():
        if "df" not in locals():

            df = pd.DataFrame.from_dict(values)
            df["player"] = key
            df["round"] = df.index.values
        else:
            try:
                dat = pd.DataFrame.from_dict(values)
            except ValueError as ve:
                print(values.values())
                continue
            dat["player"] = key
            dat["round"] = dat.index.values
            df = pd.concat([df, dat], axis=0)

    return df.melt(
        id_vars=["player", "team", "round", "opponents"],
        value_name="value",
        var_name="stat",
    ).reset_index()


def main():

    for year in range(1986, 2022):
        get_game_by_game_stats(year=year).to_parquet(
            f"AFL/data/afl_table_data/AFL-Tables_game-by-game-stats_{year}.parquet"
        )


if __name__ == "__main__":
    main()
