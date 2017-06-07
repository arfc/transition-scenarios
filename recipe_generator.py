# Imports a tab delimited data file containing
# reactor data to output formatted input for
# Cycamore Reactors.
import csv
import jinja2
import sys

# Check number of input arguments
if len(sys.argv) < 3:
    print('Usage: python recipe_generator.py [Fleetcomp]\
          [ReactorTemplate]')


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
    output_template: jinja template object
    """
    with open(in_template, 'r') as default:
        output_template = jinja2.Template(default.read())
    return output_template


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
                                      power_cap=in_list[col][1])
        with open('./cyclus_input/reactors/' +
                  in_list[col][0].replace(' ', '_') +
                  '.xml', 'w') as output:
            output.write(rendered)


def main(in_csv, reactor_template):
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
    data_list = import_csv(in_csv)
    write_reactors_xml(data_list, load_template(reactor_template))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
