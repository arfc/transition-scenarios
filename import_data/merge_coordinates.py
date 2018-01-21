import csv
from fuzzywuzzy import fuzz
import sqlite3 as sql


def get_cursor(file_name):
    """ Connects and returns a cursor to an sqlite output file

    Parameters
    ----------
    file_name: str
        name of the sqlite file

    Returns
    -------
    sqlite cursor3
    """
    con = sql.connect(file_name)
    con.row_factory = sql.Row
    return con.cursor()


def merge_coordinates(pris_link, scrape):
    pris = []
    with open(pris_link, encoding='utf-8') as src:
        reader = csv.reader(src, delimiter=',')
        pris.extend(reader)
        cur = get_cursor(scrape)
        coords = cur.execute(
            "SELECT name, long, lat FROM reactors_coordinates")
        for web in coords:
            for prs in pris[1:]:
                if fuzz.partial_ratio(web['name'].lower(),
                                      prs[1].lower()) > 70:
                    prs[13] = web['lat']
                    prs[14] = web['long']
    with open('pris_coordinates.csv', 'w') as output:
        writer = csv.writer(output, delimiter=',')
        writer.writerows(pris)
