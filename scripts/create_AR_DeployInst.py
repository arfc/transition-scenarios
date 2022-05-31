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
    deployed_dict = {}
    deployed_dict = {'lifetime': [],
                 'prototype': [],
                 'n_build': [],
                 'build_times': []}
    for indx, val in enumerate(deployinst_dict['DeployInst']['prototypes']['val']):
        if val in power_dict.keys():
            deployed_dict['prototype'].append(val)
            #deployed_dict['lifetime'].append(int(i['config']['DeployInst']['lifetimes']['val'][indx]))
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

def get_lifetime(name, path):
    ''''
    Get the lifetime of a prototype from a modular file of the prototype 
    definition

    Parameters:
    -----------
    name: str
        name of prototype
    path: str
        relative path to prototype definition file
    Returns:
    --------
    lifetime: int
        lifetime of prototype
    '''
    prototype_dict = convert_xml_to_dict(path + name +'.xml')
    lifetime = int(prototype_dict['facility']['lifetime'])
    return lifetime

def insert_lifetimes(path, deployed_dict):
    ''''
    Uses get_lifetime to get the lifetime of each prototype in the 
    deployed_dict, then inserts the lifetime into the lifetime 
    key of the deployed_dict
    
    Parameters:
    ----------
    path: str
        path to file defining prototype
    deployed_dict: dict
        dictionary of information for the DeployInst

    Returns:
    --------
    deployed_dict: dict
        udpated dictionary of information for the DeployInst
        with the lifetime of each prototype
    '''
    for key in deployed_dict['prototype']:
        deployed_dict['lifetime'].append(get_lifetime(key, path))
    return deployed_dict

def legacy_lifetimes(d, extension_eq, region_indx=1):
    new_xml = copy.deepcopy(d)
    # default has been 60 years = 720 timesteps
    for i in range(len(new_xml['simulation']['region']['institution'][0]['config']['DeployInst']['lifetimes']['val'])):
        x = eval(extension_eq)
        new_xml['simulation']['region']['institution'][0]['config']['DeployInst']['lifetimes']['val'][i] = str(int(new_xml['simulation']['region'][1]['institution'][0]['config']['DeployInst']['lifetimes']['val'][i]) + x)
    return new_xml


def get_deployed_power(power_dict, deployed_dict, sim_duration):
    '''
    Creates array of the total power from agents in a given 
    DeployInst. Each entry in the array is for each time step in 
    the simulation.

    Parameters:
    -----------
    power_dict: dict
        contains the power output of each agent in the DeployInst
    deployed_dict: dict
        contains the lifetimes, number built, and name of each 
        prototype in the DeployInst
    sim_duration: int
        number of timesteps in the simulation

    Returns:
    --------
    t: array
        ranged arrays of durations
    inst_power: array 
        deployed power at each timestep from a single DeployInst 
        based on the power and duration of each prototype
    '''
    t = np.arange(sim_duration)
    for key, val in deployed_dict.items():
        power_profile = np.zeros(len(t))
        for i, v in enumerate(deployed_dict['prototype']):
            prototype_power = np.zeros(len(t))
            prototype_power[deployed_dict['build_times'][i] : deployed_dict['build_times'][i] + deployed_dict['lifetime'][i]] += power_dict[v] * deployed_dict['n_build'][i]
            power_profile += prototype_power   
    return t, power_profile
    

def determine_power_gap(power_profile, demand):
    '''
    Calculates the amount of power needed to be supplied 
    based on the power produced and the demand equation

    Parameters:
    ----------
    power_profile: array
        Amount of power produced at each time step
    demand: array
        evaluated values of the power demand equation used

    Returns:
    --------
    power_gap: array
        Amount of power needed to meet the power demand. Any negative 
        values from an oversupply of power are changed to 0
    '''
    power_gap = demand - power_profile
    power_gap[power_gap < 0] = 0
    return power_gap 
    
if __name__ == '__main__':
    simulation_input = "../input/haleu/inputs/united_states_2020.xml"
    deployinst_input = "../input/haleu/inputs/united_states/buildtimes/UNITED_STATES_OF_AMERICA/deployinst.xml"
    prototype_path = "../input/haleu/inputs/united_states/reactors/"

    #Create dictionaries
    simulation_dict = convert_xml_to_dict(simulation_input)
    deployinst_dict = convert_xml_to_dict(deployinst_input)

    # get information out of dictionaries 
    duration = get_simulation_duration(simulation_dict)
    lwr_powers = get_pris_powers('UNITED STATES OF AMERICA', 2020)
    deployed_lwr_dict = get_deployinst_dict(deployinst_input, lwr_powers)
    deployed_lwr_dict = insert_lifetimes(prototype_path, deployed_lwr_dict)

    #Figure out power already deployed and power needed
    time, deployed_power = get_deployed_power(lwr_powers, deployed_lwr_dict, duration)

    #Figure out how many new prototypes are needed
    