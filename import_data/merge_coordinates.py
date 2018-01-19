import sys
sys.path.append('./..')
sys.path.append('./../analysis')

import analysis as an
import import_pris as ip
import csv
from fuzzywuzzy import fuzz
import sqlite3 as sql


def merge_coordinates(pris, scrape):
	pris = []
    with open(pris, encoding='utf-8') as src:
        reader = csv.reader(src, delimiter=',')
        pris.extend(reader)
        cur = an.get_cursor(pris)
        coords = cur.execute("SELECT name, long, lat FROM reactors_coordinates")
        for web, prs in zip(coords, pris):
            if fuzz.partial_ratio(web['name'].lower(),prs[1].lower()) > 80:
            	prs[13] = double(web['long'])
            	prs[14] = double(web['lat'])
                	
                
    return reader


# [13]: Long [14]: Lat
