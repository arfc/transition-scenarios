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
# import output as oup
# ----------------------------
# Parse Dakota parameters file
# ----------------------------

params, results = di.read_parameters_file()

# -------------------------------
# Convert and send to Cyclus
# -------------------------------

# Edit Cyclus input file
cyclus_template = 'lwr_lifetime_input.xml.in'
scenario_name = 'lwr_' + str(round(params['lwr']))
variable_dict = {'handle': scenario_name,
                 'lwr_lifetime': str(int(params['lwr']))}
output_xml = './cyclus-files/lwr_lifetime_' + str(params['lwr']) + '.xml'
inp.render_input(cyclus_template, variable_dict, output_xml)

# Create DeployInst for LWRs
DI_dict = oup.write_lwr_deployinst(params['lwr'])
cdi.write_deployinst(DI_dict, './cyclus-files/lwr_' +
                        str(int(params['lwr'])) + '_deployinst.xml')

# Create DeployInst for advanced reactors
duration = 1500
reactor_prototypes = {'Xe-100': (76, 720), 'MMR': (5, 240), 'VOYGR': (73, 720)}
demand_equation = np.zeros(duration)
demand_equation[721:] = 87198.156
lwr_DI = cdi.convert_xml_to_dict("./cyclus-files/lwr_" +
                                 str(int(params['lwr'])) +
                                 '_deployinst.xml')
deploy_schedule = cdi.write_AR_deployinst(lwr_DI,
                                          duration, 
                                          reactor_prototypes, 
                                          demand_equation)
cdi.write_deployinst(deploy_schedule, 
                     "./cyclus-files/AR_DeployInst_lwr_" +
                     str(int(params['lwr'])) + ".xml")


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
