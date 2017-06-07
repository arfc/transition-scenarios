# Imports a tab delimited data file containing
# reactor data to output formatted input for
# Cycamore Reactors.
from pyne import nucname as nn
import csv
import jinja2
import sys

# Check number of input arguments
if len(sys.argv) < 3:
    print('Usage: python recipe_generator.py [Fleetcomp]\
          [ReactorTemplate]')


def import_csv(in_csv):
    """ Imports contents of a comma delimited csv file
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


def load_template(in_template):
    """ Returns a jinja2 template.

    Parameters
    ---------
    in_template: str
        template file name.

    Returns
    -------
    output_template: jinja template object
    """
    with open(in_template, 'r') as default:
        output_template = jinja2.Template(default.read())
    return output_template


def get_composition(in_list, burnup):
    """ Returns a dictionary of reactor name and build_time (in months)
    using the fleetcomp list for reactors specified in *args.

    Parameters
    ---------
    in_list: list
        list file containing fleetcomp data.
    *args: str
        path and name of reactors that will be added to cyclus simulation.

    Returns
    -------
    data_dict: dictionary
        dictionary with key: isotope, and value: composition.
    """
    data_dict = {}
    for i in range(len(in_list)):
        if i > 1:
            if burnup == '33':
                data_dict.update({nn.id(in_list[i][0]):
                                  in_list[i][2]})
            elif burnup == '51':
                data_dict.update({nn.id(in_list[i][0]):
                                  in_list[i][4]})
            else:
                data_dict.update({nn.id(in_list[i][0]):
                                  in_list[i][6]})
    return data_dict


def write_recipes(in_dict, in_template, burnup):
    """ Renders jinja template using data from in_list and
    outputs an xml file for a single reactor.

    Parameters
    ---------
    data_dict: dictionary
        dictionary with key: isotope, and value: composition.
    in_template: jinja template object
        jinja template object to be rendered.

    Returns
    -------
    null
        generates reactor files for cyclus.
    """
    isotope_list = in_dict.keys()
    composition_list = in_dict.values()
    rendered = in_template.render(id=isotope_list,
                                  comp=composition_list)
    with open('./cyclus_input/recipes/uox_' +
              burnup +
              '.xml', 'w') as output:
                output.write(rendered)


def main(in_csv, recipe_template, burnup):
    """ Generates reactor xml input for cyclus.

    Parameters
    ---------
    in_csv: str
        csv file name.
    reactor_template: str
        template file name.

    Returns
    -------
    null
        generates reactor files for all reactors specified in in_csv file.
    """
    write_recipes(get_composition(import_csv(in_csv), burnup),
                  load_template(recipe_template), burnup)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
