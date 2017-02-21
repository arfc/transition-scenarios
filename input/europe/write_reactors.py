import jinja2
import mimetypes
import numpy as np
import os
import smtplib
import sys
import getpass
import pandas as pd
from io import StringIO
import csv
#to run: 
#		python write_reactors.py [csv_file] [template_file]

#takes second argument file as template

with open(sys.argv[2],'r') as fp:
	input_template = fp.read()
	template = jinja2.Template(input_template)

reactor_lists = np.genfromtxt(sys.argv[1],
	delimiter=',',
	dtype=('S128','S128','float64','float64'),
	names=('country','reactor_name','n_assem_core','n_assem_batch'))


#takes first argument file and saves reactor_name, num_assem_core, num assem_batch as array.
#reactor_lists = np.loadtxt(sys.argv[1],
#	delimiter=',',
#	dtype={'names':('reactor_name','n_assem_core','n_assem_batch'),
#		'formats': ('S128', 'S128', 'S128')})

#creates a file (**if already there simply appends!**) called written_input_file and writes the results
output=open('written_input_file.xml','a')
print(reactor_lists)

#for every row, replace the following items with values in the csv file.
for reactor in reactor_lists:
	reactor_body = template.render(country=reactor['country'],reactor_name=reactor['reactor_name'], n_assem_core=reactor['n_assem_core'], n_assem_batch=reactor['n_assem_batch'])
	output.write(reactor_body)

