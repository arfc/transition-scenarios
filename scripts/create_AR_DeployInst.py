import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#plt.rcParams['image.cmap'] = 'viridis'
import xmltodict
from pprint import pprint
import copy
#src_path = './src'

def convert_xml_to_dict(filename):
    '''
    Reads in an xml file and converts it to a python dictionary

    Parameters:
    -----------
    filename: str
        name of xml file
    
    Returns:
    --------
    xml_dict: dict of strings
        contents of the xml file as a dictionary
        
    '''
    xml_dict = xmltodict.parse(open(filename, 'r').read())
    return xml_dict


def get_deployinst_dict(deployinst_dict, power_dict):
    '''
    Removes any non-power producing prototypes from the dictionary of 
    the DeployInst. This also removes the 'val' level of information. 
    Returns a dictionary about deployment information from the Inst.
    This function assumes the input for a single DeployInst is provided.
    Only the the prototype names that are in the power_dict are included 
    in the output, so that only prototypes that produce power are considered. 

    Parameters:
    -----------
    deployinst_dict: dict
        dictionary of DeployInst information
    reactor_dict: dict
        dictionary of LWR prototype names
    
    Returns:
    --------
    deployed_dict: dict
        dictionary of information about LWR prototypes and
        their deployment
    '''
    # get enter / lifetimes / n_builds
    # Still need to actually change function
    deployed_dict = {}
    deployed_dict[i['name']] = {'lifetime': [],
                 'prototype': [],
                 'n_build': [],
                 'build_times': []}
    for indx, val in enumerate(deployinst_dict['DeployInst']['prototypes']['val']):
        if val in power_dict.keys():
            deployed_dict['prototype'].append(val)
            #deployed_dict[i['name']]['lifetime'].append(int(i['config']['DeployInst']['lifetimes']['val'][indx]))
            deployed_dict['n_build'].append(int(deployinst_dict['DeployInst']['n_build']['val'][indx]))
            deployed_dict['build_times'].append(int(deployinst_dict['DeployInst']['build_times']['val'][indx]))
    return deployed_dict

def get_simulation_duration(simulation_dict):
    '''
    Reads the dictionary provided to obtain the total duration of the 
    simulation

    Parameters:
    -----------
    simulation_dict: dict of strs
        dictionary of the cylus input file
    
    Returns:
    --------
    sim_duration: int
        duration of cyclus simulation
    '''
    sim_duration = int(simulation_dict['simulation']['control']['duration'])
    return sim_duration

def get_pris_powers(country, year):
    '''
    Create dictionary of the reactors units from a select country 
    in the PRIS database and 
    their corresponding rated power 
    output from the reactors_pris_XXXX.csv file for the corresponding year

    Parameters:
    -----------
    country: str
        name of country to get LWR data for
    year: int
        year of data to pull from 
    
    Returns:
    --------
    pris_power: dict 
        dictionary of reactor names and rated powers, the keys are the reactor 
        names (strs), the values are the rated powers (ints)
    '''
    pris_power = {}
    reactors = pd.read_csv('../database/reactors_pris_' + str(year) +'.csv')
    reactors = reactors.loc[reactors['Country'] == country]
    for index, row in reactors.iterrows():
        pris_power[row['Unit']] = row['RUP [MWe]']
    return pris_power


def legacy_lifetimes(d, extension_eq, region_indx=1):
    new_xml = copy.deepcopy(d)
    # default has been 60 years = 720 timesteps
    for i in range(len(new_xml['simulation']['region']['institution'][0]['config']['DeployInst']['lifetimes']['val'])):
        x = eval(extension_eq)
        new_xml['simulation']['region']['institution'][0]['config']['DeployInst']['lifetimes']['val'][i] = str(int(new_xml['simulation']['region'][1]['institution'][0]['config']['DeployInst']['lifetimes']['val'][i]) + x)
    return new_xml


def get_deployed_power(power_dict, deployed_dict, sim_duration):
    '''
    t = ranged arrays of durations
    inst_power = dictionary of each institution and their deployed power based on 
    the power and duration of each prototype
    '''
    t = np.arange(sim_duration)
    inst_power = {}
    for key, val in deployed_dict.items():
        inst_power[key] = np.zeros(len(t))
        for i, v in enumerate(val['prototype']):
            inst_power[key][deployed_dict[key]['build_times'][i] : deployed_dict[key]['build_times'][i] + deployed_dict[key]['lifetime'][i]] += power_dict[v] * deployed_dict[key]['n_build'][i]
    return t, inst_power
    

def deploy_to_meet_demand(d, a, z, demand_eq, proto_list, ratio_list, lifetime_list, newinst_name):
    filtered =  ''.join(x for x in demand_eq if x.isalpha())
    if len(filtered) != 0 and 'x' not in filtered:
        print(filtered)
        raise ValueError('The variable is `x`')
        
    power_dict, deployed_dict, duration = get_config_dict(d)
    t, inst_power = get_deployed_power(power_dict, deployed_dict, duration)
    power = np.zeros(duration)
    for key, val in inst_power.items():
        power += val
    # find lack
    demand = np.zeros(len(t))
    demand[a:z] = [eval(demand_eq) for x in t[a:z]]
    #print('demand')
    #print(demand[a:z])
    lack = demand - power
    lack[0] = 0
    ratio_list = np.array(ratio_list)
    ratio_list = ratio_list / sum(ratio_list)
    lifetime_dict = {proto_list[i]: lifetime_list[i] for i, v in enumerate(lifetime_list)}
    deploy_dict = {k:np.zeros(len(t)) for k in proto_list}
    # split lack
    lack_dict = {proto_list[i]: lack * ratio_list[i] for i, v in enumerate(ratio_list)}
    for proto, l in lack_dict.items():
        p = power_dict[proto]
        life = lifetime_dict[proto]
        for indx in range(duration):
            while lack_dict[proto][indx] > 0:
                deploy_dict[proto][indx] += 1
                lack_dict[proto][indx: indx+life] -= p
    
    append_d = {'name': newinst_name,
                'config': {'DeployInst': {'prototypes': {'val': []},
                                          'n_build': {'val': []},
                                          'build_times': {'val': []},
                                          'lifetimes': {'val': []}}
                            }
               }
    tot = 0
    for key in deploy_dict:
        for indx, val in enumerate(deploy_dict[key]):
            if val == 0:
                continue
            tot += 1
            append_d['config']['DeployInst']['prototypes']['val'].append(key)
            append_d['config']['DeployInst']['n_build']['val'].append(int(val))
            append_d['config']['DeployInst']['build_times']['val'].append(int(indx))
            append_d['config']['DeployInst']['lifetimes']['val'].append(int(lifetime_dict[key]))
   
    if tot == 0:
        return copy.deepcopy(d)
        #for i in range(3):
        #    append_d['config']['DeployInst']['prototypes']['val'].append('dummy')
        #    append_d['config']['DeployInst']['n_build']['val'].append(1)
        #    append_d['config']['DeployInst']['build_times']['val'].append(1)
        #    append_d['config']['DeployInst']['lifetimes']['val'].append(1)
    

    new_xml = copy.deepcopy(d)
    new_xml['simulation']['region']['institution'].append(append_d)
    return new_xml

def stacked_bar(x, y):
    fig = plt.figure()
    a2 = fig.add_subplot(111)
    prev = copy.deepcopy(np.zeros(len(x)))
    for key, val in y.items():
        a2.bar(x, height=val, width=1, bottom=prev, label=key+' power')
        prev += val
    a2.set_title('Power capacity')
    a2.set_xlabel('Timesteps')
    a2.set_ylabel('Power Capacity')
    a2.grid()
    a2.legend()
    print('show')
    plt.show()
    
if __name__ == '__main__':
    simulation_input = "../input/haleu/inputs/united_states_2020.xml"
    deployinst_input = "../input/haleu/inputs/united_states/buildtimes/UNITED_STATES_OF_AMERICA/deployinst.xml"

    simulation_dict = convert_xml_to_dict(simulation_input)
    deployinst_dict = convert_xml_to_dict(deployinst_input)

    duration = get_simulation_duration(simulation_dict)
    lwr_powers = get_pris_powers('UNITED STATES OF AMERICA', 2020)
    deployed_lwr_dict = get_deployinst_dict