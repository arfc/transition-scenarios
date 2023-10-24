import numpy as np
import subprocess
import dakota.interfacing as di
import sys
import os
from turtle import up
sys.path.append('../../../../../scripts')
import dakota_input as inp
import output_metrics as oup
import create_AR_DeployInst as cdi
# ----------------------------
# Parse Dakota parameters file
# ----------------------------

params, results = di.read_parameters_file()

# -------------------------------
# Convert and send to Cyclus
# -------------------------------

# Edit Cyclus input file
cyclus_template = 'xe100_share_mmr_burnup_input.xml.in'
scenario_name = 'xe100_share_' + \
    str(int(params['xe100_share'])) + '_mmr_burnup_' + str(int(params['mmr_burnup']))
variable_dict = {'handle': scenario_name,
                 'xe100_share': str(int(params['xe100_share'])),
                 'mmr_burnup': str(int(params['mmr_burnup']))}
output_xml = './cyclus-files/' + scenario_name + '.xml'

output_sqlite = './cyclus-files/' + scenario_name + '.sqlite'
inp.render_input(cyclus_template, variable_dict, output_xml)

# Create DeployInst for advanced reactors
duration = 1500
mmr_lifetimes = {41: 120, 62: 180, 74: 218, 78: 231, 82: 240, 86: 255, 90: 267}
reactor_prototypes = {'Xe-100': (76, 720),
                      'MMR': (5, mmr_lifetimes[int(params['mmr_burnup'])]),
                      'VOYGR': (73, 720)}
demand_equation = np.zeros(duration)
demand_equation[721:] = 87198.156
lwr_DI = cdi.convert_xml_to_dict(
    "../../../inputs/united_states/buildtimes/UNITED_STATES_OF_AMERICA/deployinst.xml")
deploy_schedule = cdi.write_AR_deployinst(
    lwr_DI,
    "../../../inputs/united_states/reactors/",
    duration,
    reactor_prototypes,
    demand_equation,
    {'Xe-100': int(params['xe100_share'])})
cdi.write_deployinst(deploy_schedule, "./cyclus-files/" +
                     scenario_name +
                     "_deployinst.xml")

# Run Cyclus with edited input file
oup.run_cyclus(output_sqlite, output_xml)

# ----------------------------
# Return the results to Dakota
# ----------------------------
results = oup.get_all_results(results, output_sqlite)
