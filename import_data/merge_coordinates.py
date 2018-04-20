from fuzzywuzzy import fuzz
import numpy as np
import pandas as pd
import sqlite3 as sql
import sys

if len(sys.argv) < 3:
    print('Usage: python merge_coordinates.py [pris_link] [webscrape_link]')


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


def import_pris(pris_link):
    pris = pd.read_csv(pris_link,
                       delimiter=',',
                       encoding='iso-8859-1'
                       )
    pris.insert(13, 'Latitude', np.nan)
    pris.insert(14, 'Longitude', np.nan)
    pris = pris.replace(np.nan, '')
    return pris


def import_webscrape_data(scrape_link):
    cur = get_cursor(scrape_link)
    coords = cur.execute("SELECT name, long, lat FROM reactors_coordinates")
    return coords


def get_edge_cases():
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
              'HADDAM NECK': 'Connecticut Yankee',
              'HIGASHI DORI-1 (TOHOKU)': 'Higashidōri',
              }
    return others


def sanitize_webscrape_name(name):
    blacklist = ['nuclear', 'power',
                 'plant', 'generating',
                 'station', 'reactor', 'atomic',
                 'energy', 'center', 'electric']
    name = name.lower()
    for blacklisted in blacklist:
        name = name.replace(blacklisted, '')
    name = name.strip()
    name = ' '.join(name.split())
    return name


def merge_coordinates(pris_link, scrape_link):
    others = get_edge_cases()
    pris = import_pris(pris_link)
    coords = import_webscrape_data(scrape_link)
    for web in coords:
        for idx, prs in pris.iterrows():
            webscrape_name = sanitize_webscrape_name(web['name'])
            pris_name = prs[1].lower()
            if fuzz.ratio(webscrape_name, pris_name) > 64:
                prs[13] = web['lat']
                prs[14] = web['long']
            else:
                for other in others.keys():
                    edge_case_key = other.lower()
                    edge_case_value = others[other].lower()
                    if (fuzz.ratio(pris_name, edge_case_key) > 80 and
                            fuzz.ratio(webscrape_name, edge_case_value) > 75):
                        prs[13] = web['lat']
                        prs[14] = web['long']
    return pris


def save_output(pris):
    pris.to_csv('reactors_pris_2016.csv',
                index=False,
                sep=',',
                )


def main(pris_link, scrape_link):
    pris = merge_coordinates(pris_link, scrape_link)
    save_output(pris)


if __name__ == "__main__":
    # print(import_pris(sys.argv[1]))
    main(sys.argv[1], sys.argv[2])
