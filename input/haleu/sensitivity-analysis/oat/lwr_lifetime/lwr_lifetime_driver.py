import sys
import os
from turtle import up
sys.path.append('../../../../../scripts')
import dakota_input as inp
import dakota_output as oup
# import output as oup
import dakota.interfacing as di
import subprocess
import create_AR_DeployInst as cdi
import numpy as np
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
variable_dict = {'handle': scenario_name, 'lwr_lifetime':str(int(params['lwr']))}
output_xml = './cyclus-files/lwr_lifetime.xml'
inp.render_input(cyclus_template, variable_dict, output_xml)

# Create DeployInst for LWRs
DI_dict = cdi.convert_xml_to_dict("initial_lwr_deployinst.xml")
DI_dict['DeployInst']['lifetimes'] = {'val':[]}
DI_dict['DeployInst']['lifetimes']['val'] = np.repeat(720, 116)
DI_dict['DeployInst']['lifetimes']['val'][0] = 600

with open("../../../../../database/lwr_power_order.txt", 'r') as f:
    lwrs = f.readlines()
for index, item in enumerate(lwrs):
    lwrs[index] = item.strip("\n")
lwrs_extended = lwrs[:int(params['lwr'])]

for lwr in lwrs_extended:
    index = DI_dict['DeployInst']['prototypes']['val'].index(lwr)
    DI_dict['DeployInst']['lifetimes']['val'][index] = 840
cdi.write_deployinst(DI_dict, './cyclus-files/lwr_' + str(int(params['lwr'])) + '_deployinst.xml')

# Create DeployInst for advanced reactors 
duration = 1500
reactor_prototypes = {'Xe-100':(75, 720), 'MMR':(10,240), 'VOYGR':(50, 720)}
demand_equation = np.zeros(duration)
demand_equation[721:] = 89456.55
deployinst = cdi.convert_xml_to_dict("./cyclus-files/lwr_"+str(int(params['lwr'])) + '_deployinst.xml')
lwr_powers = cdi.get_pris_powers('UNITED STATES OF AMERICA',"../../../../../database/", 2020)
deployed_lwr_dict = cdi.get_deployinst_dict(deployinst, lwr_powers, "../../../inputs/united_states/reactors/")
time, deployed_power = cdi.get_deployed_power(lwr_powers, deployed_lwr_dict, duration)
power_gap = cdi.determine_power_gap(deployed_power, demand_equation)
deploy_schedule = cdi.determine_deployment_schedule(power_gap, reactor_prototypes)
cdi.write_deployinst(deploy_schedule, "./cyclus-files/AR_DeployInst_lwr_" + str(int(params['lwr'])) +".xml")

# Run Cyclus with edited input file
output_sqlite = './cyclus-files/' + scenario_name + '.sqlite'
os.system('rm ' + output_sqlite)
os.system('cyclus -i ' + output_xml + ' -o ' + output_sqlite + \
    ' --warn-limit 2')

# ----------------------------
# Return the results to Dakota
# ----------------------------
results['enr_u'].function = oup.get_enriched_u_mass(output_sqlite, 
                                                    ['Xe-100','MMR','VOYGR'],
                                                    721)
results['haleu'].function = oup.get_enriched_u_mass(output_sqlite, 
                                                    ['Xe-100','MMR'],
                                                    721)
results['swu'].function = oup.calculate_swu(output_sqlite, ['Xe-100','MMR','VOYGR'],
                                            721)
results['haleu_swu'].function = oup.calculate_swu(output_sqlite, ['Xe-100','MMR'],
                                            721)
results['waste'].function = oup.get_waste_discharged(output_sqlite, 
                                                    ['Xe-100','MMR','VOYGR'],
                                                    721,
                                                    {'MMR':'spent_MMR_haleu',
                                                    'Xe-100':'spent_xe100_haleu',
                                                    'VOYGR':'spent_smr_fuel'}
                                                    )
results['feed'].function = oup.calculate_feed(output_sqlite, 
                                             ['Xe-100','MMR'],
				             721)
			          
results.write()
