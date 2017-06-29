import csv
import jinja2
import os
import sys

if len(sys.argv) < 5:
    print('Usage: python deploy_reactors.py [fleet]\
          [DeployinstTemplate] [InclusionsTemplate]\
          [Reactor1] [Reactor2] ...')


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
        sourcereader = csv.reader(source, delimiter='\t')
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
    output_template: jinja template object.
    """
    with open(in_template, 'r') as default:
        output_template = jinja2.Template(default.read())
    return output_template


def get_build_time(in_list, *args):
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
        dictionary with key: reactor name, and value: buildtime.
    """
    data_dict = {}
    for col, item in enumerate(in_list):
        start_date = [in_list[col][11], in_list[col][9], in_list[col][10]]
        month_diff = int((int(start_date[0])-1965) * 12 +
                         int(start_date[1]) +
                         int(start_date[2]) / (365/12))
        for index, reactor in enumerate(args[0][0]):
            fleet_name = in_list[col][0].replace(' ', '_')
            file_name = reactor.replace(os.path.dirname(args[0][0][index]), '')
            file_name = file_name.replace('/', '')
            if (fleet_name + '.xml' == file_name):
                data_dict.update({fleet_name: month_diff})
    return data_dict


def make_recipe(in_dict, deployinst_template, inclusions_template):
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
    reactor_list = in_dict.keys()
    buildtime_list = in_dict.values()
    rendered_deployinst = deployinst_template.render(reactors=reactor_list,
                                                     buildtimes=buildtime_list)
    rendered_inclusions = inclusions_template.render(reactors=reactor_list)
    with open('cyclus_input/buildtimes/deployinst.xml', 'w') as output1:
            output1.write(rendered_deployinst)
    with open('cyclus_input/buildtimes/inclusions.xml', 'w') as output2:
            output2.write(rendered_inclusions)


def main(in_csv, deployinst_template, inclusions_template, *args):
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
    if os.path.isdir(args[0][0]):
        lists = []
        for files in os.listdir(args[0][0]):
            lists.append(args[0][0] + files)
        main(in_csv, deployinst_template, inclusions_template, lists)
    else:
        fleet_list = import_csv(in_csv)
        deployinst_temp = load_template(deployinst_template)
        inclusions_temp = load_template(inclusions_template)
        buildtime_dict = get_build_time(fleet_list, args)
        make_recipe(buildtime_dict, deployinst_temp, inclusions_temp)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
