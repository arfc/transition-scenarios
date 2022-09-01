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
# import output as oup
# ----------------------------
# Parse Dakota parameters file
# ----------------------------

params, results = di.read_parameters_file()

# -------------------------------
# Convert and send to Cyclus
# -------------------------------

# Edit Cyclus input file
cyclus_template = 'voygr_share_input.xml.in'
scenario_name = 'voygr_' + str(round(params['voygr']))
variable_dict = {'handle': scenario_name, 'voygr': str(int(params['voygr']))}
output_xml = './cyclus-files/voygr_share_' + str(params['voygr']) + '.xml'
inp.render_input(cyclus_template, variable_dict, output_xml)

# Create DeployInst for advanced reactors
duration = 1500
reactor_prototypes = {'Xe-100': (76, 720), 'MMR': (5, 240), 'VOYGR': (73, 720)}
demand_equation = np.zeros(duration)
demand_equation[721:] = 87198.156
lwr_DI = cdi.convert_xml_to_dict("../../../inputs/united_states/buildtimes/UNITED_STATES_OF_AMERICA/deployinst.xml")

deploy_schedule = cdi.write_AR_deployinst(lwr_DI,
                                          duration, 
                                          reactor_prototypes, 
                                          demand_equation,
                                          'VOYGR',
                                          int(params['voygr']))
cdi.write_deployinst(deploy_schedule, 
                     "./cyclus-files/voygr_" +
                     str(int(params['voygr'])) + "_deployinst.xml")

# Run Cyclus with edited input file
output_sqlite = './cyclus-files/' + scenario_name + '.sqlite'
os.system('rm ' + output_sqlite)
os.system('cyclus -i ' + output_xml + ' -o ' + output_sqlite +
          ' --warn-limit 2')

# ----------------------------
# Return the results to Dakota
# ----------------------------
results['enr_u'].function = oup.get_enriched_u_mass(output_sqlite,
                                                    ['Xe-100', 'MMR', 'VOYGR'],
                                                    721)
results['haleu'].function = oup.get_enriched_u_mass(output_sqlite,
                                                    ['Xe-100', 'MMR'],
                                                    721)
results['swu'].function = oup.calculate_swu(
    output_sqlite, ['Xe-100', 'MMR', 'VOYGR'], 721)
results['haleu_swu'].function = oup.calculate_swu(
    output_sqlite, ['Xe-100', 'MMR'], 721)
results['waste'].function = oup.get_waste_discharged(output_sqlite,
                                                     ['Xe-100', 'MMR', 'VOYGR'],
                                                     721,
                                                     {'MMR': 'spent_MMR_haleu',
                                                      'Xe-100': 'spent_xe100_haleu',
                                                      'VOYGR': 'spent_smr_fuel'}
                                                     )
results['feed'].function = oup.calculate_feed(output_sqlite,
                                              ['Xe-100', 'MMR'],
                                              721)

results.write()
