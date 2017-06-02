import jinja2
import os
import sys
import xml.etree.ElementTree as ET

if len(sys.argv) < 2:
    print('Usage: python deploy_reactors.py [reactor1] [reactor2] ....')


def get_lifetime_and_name(*args):
    data = {}
    for reactor in args[0]:
        tree = ET.parse(reactor)
        root = tree.getroot()
        data.update({root[0][0].text: root[0][1].text})
    return data


def load_template(in_template):
    with open(in_template, 'r') as default:
        output_template = jinja2.Template(default.read())
    return output_template


def make_recipe(in_dict, in_template):
    reactor_list = in_dict.keys()
    lifetime_list = in_dict.values()
    rendered = in_template.render(reactors=reactor_list,
                                  lifetimes=lifetime_list)
    with open('cyclus_input/recipes/lifetimes.xml', 'w') as output:
            output.write(rendered)


def main(*args):
    if os.path.isdir(args[0][0]):
        lists = []
        for files in os.listdir(args[0][0]):
            lists.append(args[0][0] + files)
        main(lists)
    else:
        data = get_lifetime_and_name(*args)
        input_temp = load_template('./templates/deploy_template.xml')
        make_recipe(data, input_temp)


if __name__ == "__main__":
    main(sys.argv[1:])
