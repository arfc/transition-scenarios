import sys
import os
from turtle import up
sys.path.append('../../../scripts')
import dakota_input as inp
import dakota_output as oup
# import output as oup
import dakota.interfacing as di
import subprocess
# ----------------------------
# Parse Dakota parameters file
# ----------------------------

params, results = di.read_parameters_file()

# -------------------------------
# Convert and send to Cyclus
# -------------------------------

# Edit Cyclus input file
cyclus_template = 'cyclus-files/scenario7.xml.in'
scenario_name = 'ty' + str(round(params['x1']))
variable_dict = {'handle': scenario_name, 'start_transition': int(params['x1'])}
# the start time needs to be an integer for cyclus
output_xml = 'cyclus-files/scenario7.xml'
inp.render_input(cyclus_template, variable_dict, output_xml)

# Run Cyclus with edited input file
output_sqlite = 'cyclus-files/scenario7_' + scenario_name + '.sqlite'
os.system('rm ' + output_sqlite)
os.system('cyclus -i ' + output_xml + ' -o ' + output_sqlite + \
    ' --warn-limit 2')
# ----------------------------
# Return the results to Dakota
# ----------------------------

#for i, r in enumerate(results.responses()):
#    if r.asv.function:
#        r.function = 1 #can change to evaluation script
#        print('OUT', i, r.function)
results['enr_u'].function = oup.get_enriched_u_mass(output_sqlite, params['x1'])
#results['des2']
results.write()
