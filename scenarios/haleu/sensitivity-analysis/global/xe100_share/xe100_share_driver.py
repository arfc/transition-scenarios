import numpy as np
import subprocess
import dakota.interfacing as di
import sys
import os
from turtle import up
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
cyclus_template = 'xe100_share_input.xml.in'
scenario_name = ('ts_' + str(int(params['ts'])) +
                '_lwr_' + str(int(params['lwr'])) + 
                '_xe100_share_' + str(int(params['xe100_share'])) +
                '_xe100_burnup_' + str(int(params['xe100_burnup'])) +
                '_mmr_burnup_' + str(int(params['mmr_burnup'])))
variable_dict = {'handle': scenario_name,
                 'ts': str(int(params['ts'])),
                 'lwr': str(int(params['lwr'])),
                 'xe100_share': str(int(params['xe100_share'])),
                 'mmr_burnup':str(int(params['mmr_burnup'])),
                 'xe100_burnup':str(int(params['xe100_burnup']))}
output_xml = "./cyclus-files/" + scenario_name + ".xml"
output_sqlite = './cyclus-files/' + scenario_name + '.sqlite'

mmr_lifetime = int(np.round(params['mmr_burnup'],2)*1331.73/15/30)
mmr_burnup_dict = {'mmr_lifetime':mmr_lifetime}
inp.render_input('../mmr_burnup_input.xml.in', 
                 mmr_burnup_dict, 
                 "./cyclus-files/mmr_" + str(int(params['mmr_burnup'])) + ".xml")

xe100_cycles = {28:(1,7), 32:(1,8), 48:(2,6), 56:(2,7), 64:(2,8),
                72:(3,6), 84:(3,7), 96:(3,8), 112:(4,7), 128:(4,8),
                120:(5,6), 140:(5,7), 160:(5,8), 151:(6,6), 168:(6,7),
                185:(6,8)}
xe100_burnup_dict = {'xe100_cycle':xe100_cycles[int(params['xe100_burnup'])][1],
                     'xe100_n_assem':xe100_cycles[int(params['xe100_burnup'])][0],
                     'xe100_assem':1675.44/xe100_cycles[int(params['xe100_burnup'])][0]
                    }
inp.render_input("../xe100_burnup_input.xml.in",
                 xe100_burnup_dict,
                 "./cyclus-files/xe100_" + str(int(params['xe100_burnup'])) +
                 ".xml")

inp.render_input(cyclus_template, variable_dict, output_xml)

# Create DeployInst for LWRs
DI_dict = cdi.write_lwr_deployinst(
    params['lwr'],
    "../../../inputs/united_states/buildtimes/" +
    "UNITED_STATES_OF_AMERICA/deployinst.xml",
    "../../../../../database/lwr_power_order.txt")
cdi.write_deployinst(DI_dict, './cyclus-files/' + 
                              scenario_name +
                              '_deployinst.xml')

# Create DeployInst for advanced reactors
duration = 1500
reactor_prototypes = {'Xe-100': (76, 720), 
                      'MMR': (5, mmr_lifetime), 
                      'VOYGR': (73, 720)}
demand_equation = np.zeros(duration)
demand_equation[int(params['ts']):] = 87198.156
lwr_DI = cdi.convert_xml_to_dict('./cyclus-files/' + 
                              scenario_name +
                              '_deployinst.xml')
deploy_schedule = cdi.write_AR_deployinst(
    lwr_DI,
    "../../../inputs/united_states/reactors/",
    duration,
    reactor_prototypes,
    demand_equation,
    {'Xe-100':int(params['xe100_share'])})
cdi.write_deployinst(deploy_schedule, "./cyclus-files/AR_DeployInst_" + 
                                      scenario_name +
                                      ".xml")

# Run Cyclus with edited input file
oup.run_cyclus(output_sqlite, output_xml)

# ----------------------------
# Return the results to Dakota
# ----------------------------
results = oup.get_all_results(results, output_sqlite)

os.system('rm ' + output_sqlite)
