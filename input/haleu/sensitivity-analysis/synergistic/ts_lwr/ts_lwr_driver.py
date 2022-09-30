import numpy as np
import subprocess
import dakota.interfacing as di
import sys
import os
from turtle import up
sys.path.append('../../../../../scripts')
import create_AR_DeployInst as cdi
import dakota_output as oup
import dakota_input as inp
# ----------------------------
# Parse Dakota parameters file
# ----------------------------

params, results = di.read_parameters_file()

# -------------------------------
# Convert and send to Cyclus
# -------------------------------

# Edit Cyclus input file
cyclus_template = 'ts_lwr_input.xml.in'
scenario_name = 'ts_' + str(round(params['ts'])) + '_lwr_' + \
    str(round(params['lwr']))
variable_dict = {'handle': scenario_name,
                 'ts': int(params['ts']),
                 'lwr': int(params['lwr'])}
output_xml = './cyclus-files/ts_' + str(int(params['ts'])) + '_lwr_' + \
    str(int(params['lwr'])) + '.xml'    
output_sqlite = './cyclus-files/' + scenario_name + '.sqlite'
inp.render_input(cyclus_template, variable_dict, output_xml)

# Create DeployInst for LWRs
DI_dict = cdi.write_lwr_deployinst(
    params['lwr'],
    "../../../inputs/united_states/buildtimes/" +
    "UNITED_STATES_OF_AMERICA/deployinst.xml",
    "../../../../../database/lwr_power_order.txt")
cdi.write_deployinst(DI_dict, './cyclus-files/ts_' +
                     str(int(params['ts'])) +
                     '_lwr_' +
                     str(int(params['lwr'])) +
                     '_deployinst.xml')

# Create DeployInst for advanced reactors
duration = 1500
reactor_prototypes = {'Xe-100': (76, 720), 'MMR': (5, 240), 'VOYGR': (73, 720)}
demand_equation = np.zeros(duration)
demand_equation[int(params['ts']):] = 87198.156
lwr_DI = cdi.convert_xml_to_dict("./cyclus-files/lwr_" +
                                 str(int(params['ts'])) +
                                '_lwr_' +
                                str(int(params['lwr'])) +
                                '_deployinst.xml')
deploy_schedule = cdi.write_AR_deployinst(
    lwr_DI,
    "../../../inputs/united_states/reactors/",
    duration,
    reactor_prototypes,
    demand_equation)
cdi.write_deployinst(deploy_schedule, "./cyclus-files/AR_ts_" +
                     str(int(params['ts'])) +
                     '_lwr_' +
                     str(int(params['lwr'])) +
                     "_deployinst.xml")

# Run Cyclus with edited input file
oup.run_cyclus(output_sqlite, output_xml)

# ----------------------------
# Return the results to Dakota
# ----------------------------
results = oup.get_all_results(results, output_sqlite)
