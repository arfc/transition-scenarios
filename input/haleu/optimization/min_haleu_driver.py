import numpy as np
import subprocess
import dakota.interfacing as di
import sys
import os
sys.path.append('../../../../scripts')
import create_AR_DeployInst as cdi
import output_metrics as oup
import dakota_input as inp
# import output as oup
# ----------------------------
# Parse Dakota parameters file
# ----------------------------

params, results = di.read_parameters_file()

# -------------------------------
# Convert and send to Cyclus
# -------------------------------

# Edit Cyclus input file
cyclus_template = 'oncethrough_input.xml.in'
scenario_name = ('lwr_' + 
                 str(int(params['lwr'])) + 
                 '_mmr_share_' + 
                 str(int(params['mmr_share'])) +
                 '_xe100_share_' + 
                 str(int(params['xe100_share'])) + 
                 '_voygr_share_' + 
                 str(int(params['voygr_share'])) + 
                 '_mmr_burnup_' + 
                 str(int(params['mmr_burnup'])) + 
                 '_xe100_burnup_' + 
                 str(int(params['xe100_burnup'])))
variable_dict = {'handle': scenario_name,
                 'lwr':str(int(params['lwr'])), 
                 'mmr_share':str(int(params['mmr_share'])),
                 'xe100_share':str(int(params['xe100_share'])),
                 'voygr_share':str(int(params['voygr_share'])),
                 'mmr_burnup':str(int(params['mmr_burnup'])),
                 'xe100_burnup':str(int(params['xe100_burnup']))}
output_xml = './cyclus-files/' + scenario_name + '.xml'
             
output_sqlite = './cyclus-files/' + scenario_name + '.sqlite'
inp.render_input(cyclus_template, variable_dict, output_xml)

# Create DeployInst for LWRs
DI_dict = cdi.write_lwr_deployinst(
    params['lwr'],
    "../../inputs/united_states/buildtimes/" +
    "UNITED_STATES_OF_AMERICA/deployinst.xml",
    "../../../../database/lwr_power_order.txt")
cdi.write_deployinst(DI_dict, './cyclus-files/' +
                     scenario_name + 
                     '_deployinst.xml')

# Create DeployInst for advanced reactors
duration = 1500
mmr_lifetimes = {41:120, 62:180, 74:218, 78:231, 82:240, 86:255, 90:267}
reactor_prototypes = {'Xe-100': (76, 720), 
                      'MMR': (5, mmr_lifetimes[int(params['mmr_burnup'])]), 
                      'VOYGR': (73, 720)}
demand_equation = np.zeros(duration)
demand_equation[721:] = 87198.156
lwr_DI = cdi.convert_xml_to_dict("./cyclus-files/" +
                                 scenario_name + 
                                 '_deployinst.xml')
deploy_schedule = cdi.write_AR_deployinst(
    lwr_DI,
    "../../inputs/united_states/reactors/",
    duration,
    reactor_prototypes,
    demand_equation,
    {'MMR':int(params['mmr_share']), 
     'Xe-100':int(params['xe100_share']),
     'VOYGR':int(params['voygr_share'])})
cdi.write_deployinst(deploy_schedule, "./cyclus-files/AR_DeployInst_" +
                     scenario_name + 
                     ".xml")

# Run Cyclus with edited input file
oup.run_cyclus(output_sqlite, output_xml)

# ----------------------------
# Return the results to Dakota
# ----------------------------
results['haleu_swu'].function = oup.calculate_swu(output_sqlite, 
                                                  ['Xe-100', 'MMR'],
                                                  721)
results.write()

os.system('rm ' + output_sqlite)
