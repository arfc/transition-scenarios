#This script is a basic xml parser with simple xinclude support
#using ElementTree. Mainly for convinience.
import os
import lxml.etree as ET

def parse_xml(in_xml):
    tree = ET.parse(in_xml)
    tree.xinclude()
    root = tree.getroot()

    with open(in_xml, 'wb') as output:
        output.write(ET.tostring(root, pretty_print=True))

def parse_all():
    for filename in os.listdir('./templated_output'):
        parse_xml('./templated_output/' + filename)

def main():
    parse_all()

if __name__ == "__main__":
    main()
