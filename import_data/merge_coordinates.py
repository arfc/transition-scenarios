import sys
sys.path.append('./..')
sys.path.append('./../analysis')

import analysis as an
import import_pris as ip
import csv
from fuzzywuzzy import fuzz
import sqlite3 as sql


def merge_coordinates(pris, scrape):
    with open(pris, encoding='utf-8') as src:
        reader = csv.reader(src, delimiter=',')
        countries = sorted({row[0] for row in reader})
        country_list = [w.replace('US', 'United States of America')
                        for w in countries]
        country_list = [w.replace('China', "People's Republic of China")
                        for w in countries]
        for cnt in countries:
            cur = an.get_cursor(pris)
            coords = cur.execute(
                "SELECT name, long, lat FROM reactors_coordinates "
                "WHERE country = " + cnt + " COLLATE NOCASE")

    return reader
