# Imports a tab delimited data file containing
# reactor data to output formatted input for
# Cycamore Reactors.
import csv
import jinja2
import sys

# Check number of input arguments
if len(sys.argv) < 3:
    print('Usage: python recipe_generator.py [Fleetcomp] [ReactorTemplate]\
          [BuildtimeTemplate]')


def import_csv(in_csv):
    with open(in_csv, 'r') as source:
        sourcereader = csv.reader(source, delimiter='\t')
        data_list = []
        for row in sourcereader:
            data_list.append(row)
    return data_list


def load_template(in_template):
    with open(in_template, 'r') as default:
        output_template = jinja2.Template(default.read())
    return output_template


def get_build_time(in_list):
    data_dict = {}
    for col, item in enumerate(in_list):
        start_date = [in_list[col][11], in_list[col][9], in_list[col][10]]
        month_diff = int((int(start_date[0])-1965) * 12 +
                         int(start_date[1]) +
                         int(start_date[2]) / (365/12))
        data_dict.update({in_list[col][0].replace(' ', '_'): month_diff})
    return data_dict


def write_reactors_xml(in_list, in_template):
    for col, item in enumerate(in_list):
        reactor_type = in_list[col][6]
        batch = int(in_list[col][24])
        assem_per_batch = 0
        assem_no = 0
        if reactor_type == 'BWR':
            assem_no = 732
            assem_per_batch = assem_no / batch
        else:
            assem_no = 240
            assem_per_batch = assem_no / batch
        rendered = in_template.render(name=in_list[col][0].replace(' ', '_'),
                                      lifetime=in_list[col][6],
                                      assem_size=in_list[col][8],
                                      n_assem_core=assem_no,
                                      n_assem_batch=assem_per_batch,
                                      power_cap=in_list[col][1])
        with open('./cyclus_input/reactors/' +
                  in_list[col][0].replace(' ', '_') +
                  '.xml', 'w') as output:
            output.write(rendered)


def write_buildtimes_xml(in_dict, in_template):
    reactor_list = in_dict.keys()
    buildtime_list = in_dict.values()
    rendered = in_template.render(reactors=reactor_list,
                                  buildtimes=buildtime_list)
    with open('cyclus_input/buildtimes/buildtimes.xml', 'w') as output:
            output.write(rendered)


def main(in_csv, reactor_template, buildtime_template):
    data_list = import_csv(in_csv)
    write_reactors_xml(data_list, load_template(reactor_template))
    write_buildtimes_xml(get_build_time(data_list),
                         load_template(buildtime_template))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
