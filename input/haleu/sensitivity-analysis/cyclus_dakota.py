import sys
import os
sys.path.append('../../../scripts')
import input as inp
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
scenario_name = 'transition_start' + str(round(params['x1']))
variable_dict = {'handle': scenario_name, 'power_cap': params['x1']}
output_xml = 'cyclus-files/scenario7.xml'
inp.render_input(cyclus_template, variable_dict, output_xml)

# Run Cyclus with edited input file
output_sqlite = 'cyclus-files/scenario7.sqlite'
os.system('cyclus -i ' + output_xml + ' -o ' + output_sqlite)
# ----------------------------
# Return the results to Dakota
# ----------------------------

for i, r in enumerate(results.responses()):
    if r.asv.function:
        r.function = 1
        print('OUT', i, r.function)

results.write()
