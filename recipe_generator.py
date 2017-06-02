# Imports a tab delimited data file containing
# reactor data to output formatted input for
# Cycamore Reactors.
import csv
import jinja2
import sys

# Check number of input arguments
if len(sys.argv) < 2:
    print('Usage: python recipe_generator.py [InputFileName] [TemplateName]')


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


def make_recipe(in_list, in_template):
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


def main(in_csv, in_template):
    data_list = import_csv(in_csv)
    input_temp = load_template(in_template)
    make_recipe(data_list, input_temp)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
