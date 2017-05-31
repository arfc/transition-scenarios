#This script is a basic xml parser with simple xinclude support
#using ElementTree. Mainly for convinience.

import sys
import lxml.etree as ET

# Check number of input arguments
if len(sys.argv) < 1:
    print('Usage: python xml_parser.py [XML.xml]')

def parse_xml(in_xml):
    tree = ET.parse(in_xml)
    tree.xinclude()
    root = tree.getroot()

    with open(in_xml, 'wb') as output:
        output.write(ET.tostring(root, pretty_print=True))

def main(in_xml):
    parse_xml(in_xml)

if __name__ == "__main__":
    main(sys.argv[1])
