# Imports a tab delimited data file containing
# reactor data to output formatted input for
# Cycamore Reactors.
from pyne import nucname as nn
import csv
import jinja2
import os
import sys


def import_csv(in_csv, delimit):
    """ Imports contents of a comma delimited csv file
    to a 2D list.

    Parameters
    ---------
    in_csv: str
        csv file name.
    delimit: str
        delimiter of the csv file

    Returns
    -------
    data_list: list
        list with fleetcomp data.
    """
    with open(in_csv, encoding='utf-8') as source:
        sourcereader = csv.reader(source, delimiter=delimit)
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
            if burnup == 33:
                data_dict.update({nn.id(in_list[i][0]):
                                  float(in_list[i][2])})
            elif burnup == 51:
                data_dict.update({nn.id(in_list[i][0]):
                                  float(in_list[i][4])})
            else:
                data_dict.update({nn.id(in_list[i][0]):
                                  float(in_list[i][6])})
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
    rendered = in_template.render(vision=in_dict)
    with open('cyclus/input/US/recipes/uox_' + str(burnup) +
              '.xml', 'w') as output:
        output.write(rendered)


def get_build_time(in_list, path_list):
    """ Returns a dictionary of reactor name and build_time (in months)
    using the fleetcomp list for reactors specified in *args.

    Parameters
    ---------
    in_list: list
        list file containing fleetcomp data.
    path_list: str
        path and name of reactors that will be added to cyclus simulation.

    Returns
    -------
    data_dict: dictionary
        dictionary with key: reactor name, and value: buildtime.
    """
    data_dict = {}
    for row, item in enumerate(in_list):
        start_date = [in_list[row][11], in_list[row][9], in_list[row][10]]
        month_diff = int((int(start_date[0]) - 1965) * 12 +
                         int(start_date[1]) +
                         int(start_date[2]) / (365.0 / 12))
        for index, reactor in enumerate(path_list):
            fleet_name = in_list[row][0].replace(' ', '_')
            file_name = reactor.replace(
                os.path.dirname(path_list[index]), '')
            file_name = file_name.replace('/', '')
            if (fleet_name + '.xml' == file_name):
                data_dict.update({fleet_name: month_diff})
    return data_dict


def write_deployment(in_dict, deployinst_template, inclusions_template):
    """ Renders jinja template using dictionary of reactor name and buildtime
    and outputs an xml file that uses xinclude to include the reactors located
    in cyclus_input/reactors.

    Parameters
    ---------
    in_dict: dictionary
        dictionary with key: reactor name, and value: buildtime.
    deployinst_template: jinja template object
        jinja template object to be rendered with deployinst.
    inclusions_template: jinja template object
        jinja template object to be rendered with reactor inclusions.

    Returns
    -------
    null
        generates single xml file that includes reactors specified in
        the dictionary.
    """
    rendered_deployinst = deployinst_template.render(reactors=in_dict)
    rendered_inclusions = inclusions_template.render(reactors=in_dict)
    with open('cyclus/input/US/buildtimes/deployinst.xml', 'w') as output1:
        output1.write(rendered_deployinst)
    with open('cyclus/input/US/buildtimes/inclusions.xml', 'w') as output2:
        output2.write(rendered_inclusions)


def write_reactors_xml(in_list, in_template):
    """ Renders jinja template using data from in_list and
    outputs an xml file for a single reactor.

    Parameters
    ---------
    in_list: list
        list file containing fleetcomp data.
    in_template: jinja template object
        jinja template object to be rendered.

    Returns
    -------
    null
        generates reactor files for cyclus.
    """
    for col, item in enumerate(in_list):
        reactor_type = in_list[col][6]
        batch = int(in_list[col][24])
        assem_per_batch = 0
        assem_no = 0
        assem_size = 0
        if reactor_type == 'BWR':
            assem_no = 732
            assem_per_batch = assem_no / batch
            assem_size = float(in_list[col][8]) / assem_no
        else:
            assem_no = 240
            assem_per_batch = int(assem_no / batch)
            assem_size = float(in_list[col][8]) / assem_no
        rendered = in_template.render(name=in_list[col][0].replace(' ', '_'),
                                      lifetime=in_list[col][6],
                                      assem_size=assem_size,
                                      n_assem_core=assem_no,
                                      n_assem_batch=assem_per_batch,
                                      power_cap=in_list[col][2])
        with open('cyclus/input/US/reactors/' +
                  in_list[col][0].replace(' ', '_') +
                  '.xml', 'w') as output:
            output.write(rendered)


def recipes(in_csv, recipe_template, burnup):
    """ Generates commodity composition xml input for cyclus.

    Parameters
    ---------
    in_csv: str
        csv file name.
    reactor_template: str
        template file name.

    Returns
    -------
    null
        Generates commodity composition xml input for cyclus.
    """
    write_recipes(get_composition(import_csv(in_csv, ','), burnup),
                  load_template(recipe_template), burnup)


def obtain_reactors(in_csv, reactor_template):
    """ Writes xml files for individual reactors in US fleet.

    Parameters
    ---------
    in_csv: str
        csv file name.
    reactor_template: str
        template file name.

    Returns
    -------
    null
        Writes xml files for individual reactors in US fleet.
    """
    write_reactors_xml(import_csv(in_csv, '\t'),
                       load_template(reactor_template))


def deploy_reactors(in_csv, deployinst_template, inclusions_template, path):
    """ Generates xml files that specifies the reactors that will be included
    in a cyclus simulation.

    Parameters
    ---------
    in_csv: str
        csv file name.
    deployinst_template: jinja template object
        jinja template object to be rendered with deployinst.
    inclusions_template: jinja template object
        jinja template object to be rendered with reactor inclusions.
    *args: str
        path and name of reactors that will be added to cyclus simulation.

    Returns
    -------
    null
        generates single xml file that includes reactors specified in
        the dictionary.
    """
    lists = []
    if path[-1] != '/':
        path += '/'
    for files in os.listdir(path):
        lists.append(path + files)
    fleet_list = import_csv(in_csv, '\t')
    buildtime_dict = get_build_time(fleet_list, lists)
    deployinst_temp = load_template(deployinst_template)
    inclusions_temp = load_template(inclusions_template)
    write_deployment(buildtime_dict, deployinst_temp, inclusions_temp)


def set_xml_base(cyclus_template, path, output_name):
    """ Sets xml:base attribute for cyclus input

    Parameters
    ---------
    cyclus_template: str
        path and name to cyclus input template
    path: str
        relative path to cyclus input file
    output_name: str
        name of the output file

    Returns
    -------
    null
        generates single xml file that includes reactors specified in
        the dictionary.
    """
    path = os.path.abspath(path) + '/'
    cyclus_input = load_template(cyclus_template).render(base_dir=path)
    with open(path + output_name + '.xml', 'w') as output1:
        output1.write(cyclus_input)


if __name__ == '__main__':
    recipes('import_data/vision_recipes/uox.csv',
            'templates/US/recipes_template.xml', 51)
    obtain_reactors('import_data/fleetcomp/US_Fleet.txt',
                    'templates/reactors_template.xml')
    deploy_reactors('import_data/fleetcomp/US_Fleet.txt',
                    'templates/US/deployinst_template.xml',
                    'templates/inclusions_template.xml',
                    'cyclus/input/US/reactors')
    set_xml_base('templates/US/US_template.xml',
                 'cyclus/input/',
                 'US')
