from AFL.afl_tables_scraper.player_stats import get_player_stats
from os import error
import pytest
from afl_tables_scaper import test_player_stats


def test_afl_player_stats_year_range_error():
    with pytest.raises(ValueError):
        get_player_stats(year = 0)

    with pytest.raises(ValueError):
        get_player_stats(year = 20000)
    
    with pytest.raises(ValueError):
        get_player_stats(year = 1896)

    with pytest.raises(ValueError):
        get_player_stats(year = 2022)