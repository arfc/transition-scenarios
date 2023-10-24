import sys, os

import numpy as np
import dakota.interfacing as di

sys.path.append('../../../../../scripts')

import create_AR_DeployInst as cdi
import output_metrics as oup
import dakota_input as inp
# ----------------------------
# Parse Dakota parameters file
# ----------------------------

params, results = di.read_parameters_file()

# -------------------------------
# Convert and send to Cyclus
# -------------------------------

# Edit Cyclus input file
cyclus_template = 'xe100_burnup_input.xml.in'
scenario_name = 'xe100_burnup_' + str(int(params['xe100_burnup']))
variable_dict = {'handle': scenario_name, 
                 'xe100_burnup': str(int(params['xe100_burnup']))}
output_xml = './cyclus-files/' + scenario_name + '.xml'
output_sqlite = './cyclus-files/' + scenario_name + '.sqlite'
inp.render_input(cyclus_template, variable_dict, output_xml)

# Create DeployInst for advanced reactors
duration = 1500
reactor_prototypes = {'Xe-100': (76, 720), 'MMR': (5, 240), 'VOYGR': (73, 720)}
demand_equation = np.zeros(duration)
demand_equation[721:] = 87198.156

lwr_DI = cdi.convert_xml_to_dict(
    "../../../inputs/united_states/buildtimes/UNITED_STATES_OF_AMERICA/deployinst.xml")

deploy_schedule = cdi.write_AR_deployinst(lwr_DI,
                                          "../../../inputs/united_states/reactors/",
                                          duration,
                                          reactor_prototypes,
                                          demand_equation)
cdi.write_deployinst(deploy_schedule,
                     "./cyclus-files/xe100_burnup_" +
                     str(int(params['xe100_burnup'])) + "_deployinst.xml")

# Run Cyclus with edited input file
oup.run_cyclus(output_sqlite, output_xml)

# ----------------------------
# Return the results to Dakota
# ----------------------------
results = oup.get_all_results(results, output_sqlite)
