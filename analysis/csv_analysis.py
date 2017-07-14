import csv


def import_csv(in_csv):
    """ Imports contents of a tab delimited csv file
    to a 2D list.

    Parameters
    ---------
    in_csv: str
        csv file name.

    Returns
    -------
    data_list: list
        list with fleetcomp data.
    """
    with open(in_csv, 'r') as source:
        sourcereader = csv.reader(source, delimiter=',')
        data_list = []
        for row in sourcereader:
            data_list.append(row)

    return data_list


def get_cf(in_list):
    """ Creates a list of capacity factor from
    the imported csv file
    """
    cf = []
    for row in in_list[1:]:
        for i in range(0, 12):
            cf.append(float(row[1]) / 1000)

    return cf
