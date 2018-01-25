import csv
from fuzzywuzzy import fuzz
import sqlite3 as sql
import sys


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
    others = {'OHI-': 'Ōi',
              'ASCO-': 'Ascó',
              'ROVNO-': 'Rivne',
              'SHIN-KORI-': 'Kori',
              'ANO-': 'Arkansas One',
              'HANBIT-': 'Yeonggwang',
              'FERMI-': 'Enrico Fermi',
              'BALTIC-': 'Kaliningrad',
              'COOK-': 'Donald C. Cook',
              'HATCH-': 'Edwin I. Hatch',
              'HARRIS-': 'Shearon Harris',
              'SHIN-WOLSONG-': 'Wolseong',
              'ST. ALBAN-': 'Saint-Alban',
              'LASALLE-': 'LaSalle County',
              'SUMMER-': 'Virgil C. Summer',
              'FARLEY-': 'Joseph M. Farley',
              'ST. LAURENT ': 'Saint-Laurent',
              'HADDAM NECK': 'Connecticut1 Yankee',
              'HIGASHI DORI-1 (TOHOKU)': 'Higashidōri',
              }
    blacklist = ['nuclear', 'power',
                 'plant', 'generating',
                 'station', 'reactor', 'atomic',
                 'energy', 'center', 'electric']
    with open(pris_link, encoding='utf-8') as src:
        reader = csv.reader(src, delimiter=',')
        pris.extend(reader)
        cur = get_cursor(scrape)
        coords = cur.execute(
            "SELECT name, long, lat FROM reactors_coordinates")
        for web in coords:
            for prs in pris[1:]:
                name_web = web['name'].lower()
                for blacklisted in blacklist:
                    name_web = name_web.replace(blacklisted, '')
                if fuzz.ratio(name_web.rstrip(), prs[1].lower()) > 64:
                    # print(name_web.rstrip(), ' and ', prs[1].lower())
                    prs[13] = web['lat']
                    prs[14] = web['long']
                else:
                    for other in others.keys():
                        if fuzz.ratio(prs[1].lower(), other.lower()) > 80:
                            if fuzz.ratio(others[other].lower(),
                                          name_web.rstrip().lower()) > 75:
                                # print(prs[1], ' and ', name_web.rstrip())
                                prs[13] = web['lat']
                                prs[14] = web['long']
    with open('reactors_pris_2016.csv', 'w') as output:
        writer = csv.writer(output, delimiter=',')
        writer.writerows(pris)


def main(pris, scrape):
    merge_coordinates(pris, scrape)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
