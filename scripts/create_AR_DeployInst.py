import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import xmltodict
from pprint import pprint
import math


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


def get_deployinst_dict(deployinst_dict, power_dict, path):
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
    path: str
        path to xml files for each prototype

    Returns:
    --------
    deployed_dict: dict
        dictionary of information about LWR prototypes and
        their deployment
    '''
    deployed_dict = {}
    deployed_dict = {'lifetime': [],
                     'prototypes': [],
                     'n_build': [],
                     'build_times': []}
    for indx, val in enumerate(
            deployinst_dict['DeployInst']['prototypes']['val']):
        if val in power_dict.keys():
            deployed_dict['lifetime'].append(get_lifetime(path, val))
            deployed_dict['prototypes'].append(val)
            deployed_dict['n_build'].append(
                int(deployinst_dict['DeployInst']['n_build']['val'][indx]))
            deployed_dict['build_times'].append(
                int(deployinst_dict['DeployInst']['build_times']['val'][indx]))
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


def get_pris_powers(country, path, year):
    '''
    Create dictionary of the reactors units from a select country
    in the PRIS database and
    their corresponding rated power
    output from the reactors_pris_XXXX.csv file for the corresponding year

    Parameters:
    -----------
    country: str
        name of country to get LWR data for
    path: str
        relative path to the pris csv file
    year: int
        year of data to pull from

    Returns:
    --------
    pris_power: dict
        dictionary of reactor names and rated powers, the keys are the reactor
        names (strs), the values are the rated powers (ints). Any spaces 
        in the keys are replaced with underscores.
    '''
    pris_power = {}
    reactors = pd.read_csv(path + 'reactors_pris_' + str(year) + '.csv')
    reactors = reactors.loc[reactors['Country'] == country]
    for index, row in reactors.iterrows():
        pris_power[row['Unit']] = row['RUP [MWe]']
    pris_power = {k.replace(' ', '_'):v for k, v in pris_power.items()}
    return pris_power


def get_lifetime(path, name):
    ''''
    Get the lifetime of a prototype from a modular file of the prototype
    definition

    Parameters:
    -----------
    path: str
        relative path to prototype definition file
    name: str
        name of prototype
    Returns:
    --------
    lifetime: int
        lifetime of prototype
    '''
    prototype_dict = convert_xml_to_dict(path + name + '.xml')
    lifetime = int(prototype_dict['facility']['lifetime'])
    return lifetime

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
        for i, v in enumerate(deployed_dict['prototypes']):
            prototype_power = np.zeros(len(t))
            prototype_power[deployed_dict['build_times'][i]: deployed_dict['build_times'][
                i] + deployed_dict['lifetime'][i]] += power_dict[v] * deployed_dict['n_build'][i]
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


def determine_deployment_order(reactor_prototypes):
    '''
    Creates a list of the keys in reactor_prototypes ordering
    them in decreasing order of power

    Parameters:
    ----------
    reactor_prototypes: dict
        dictionary of information about prototypes in the form
        {name(str): (power(int), lifetime(int))}

    Returns:
    --------
    reactor_order: list of strs
        ordered list of reactor prototypes in decreasing order of
        power output.
    '''
    reactor_order = []
    keys = list(reactor_prototypes.keys())
    prototypes = reactor_prototypes.copy()
    for key in keys:
        max_power_prototype = max(prototypes,
                                  key=lambda x: prototypes[x][0])
        reactor_order.append(max_power_prototype)
        prototypes.pop(max_power_prototype, None)
    return reactor_order


def determine_deployment_schedule(power_gap, reactor_prototypes):
    '''
    Define the deployemnt schedule for a single or multiple
    reactor prototypes based on a gap in production
    and demand. If multiple prototypes are provided, then
    they will be deployed in preferential order based on
    decreasing power output.

    Parameters:
    -----------
    power_gap: array
        gap in power production and demand
    reactor_prototypes: dictionary
        information about reactor prototypes to be deployed. The
        keys are the prototype names (strs) and the values are
        a tuple of the power output and lifetime (ints)

    Returns:
    --------
    deploy_schedule: dict
        deployment schedule of reactor prototypes with the
        structure for a DeployInst
    '''
    deploy_schedule = {'DeployInst': {'prototypes': {'val': []},
                                      'build_times': {'val': []},
                                      'n_build': {'val': []},
                                      'lifetimes': {'val': []}}}
    reactors = determine_deployment_order(reactor_prototypes)
    for index, value in enumerate(power_gap):
        if value <= 0:
            continue
        for reactor in reactors:
            if reactor == reactors[-1]:
                # for the last reactor round up to ensure gap is fully met, even if
                # power is slightly over supplied
                num_rxs = math.ceil(value / reactor_prototypes[reactor][0])
            else:
                num_rxs = math.floor(value / reactor_prototypes[reactor][0])
            if num_rxs == 0:
                continue
            power_gap[index:index + reactor_prototypes[reactor][1]] = \
                power_gap[index:index + reactor_prototypes[reactor]
                          [1]] - reactor_prototypes[reactor][0] * num_rxs
            deploy_schedule['DeployInst']['prototypes']['val'].append(reactor)
            deploy_schedule['DeployInst']['n_build']['val'].append(num_rxs)
            deploy_schedule['DeployInst']['build_times']['val'].append(index)
            deploy_schedule['DeployInst']['lifetimes']['val'].append(
                reactor_prototypes[reactor][1])

    return deploy_schedule


def write_deployinst(deploy_schedule, out_path):
    '''
    Write xml file for the DeployInst to meet the power demand

    Parameters:
    -----------
    deploy_schedule: dict
        deployment schedule of reactor prototypes
    out_path: str
        path to where the file should be written

    Returns:
    --------
    null
        wites xml file for Cycamore DeployInst
    '''
    with open(out_path, 'w') as f:
        f.write(xmltodict.unparse(deploy_schedule, pretty=True))


if __name__ == '__main__':
    simulation_input = "../input/haleu/inputs/united_states_2020.xml"
    deployinst_input = "../input/haleu/inputs/united_states/buildtimes/UNITED_STATES_OF_AMERICA/deployinst.xml"
    prototype_path = "../input/haleu/inputs/united_states/reactors/"
    output_path = "../input/haleu/inputs/united_states/buildtimes/advanced_reactor_deployinst.xml"
    reactor_prototypes = {'Xe-100': (75, 720),
                          'MMR': (10, 240),
                          'VOYGR': (50, 720)}

    # Create dictionaries
    simulation_dict = convert_xml_to_dict(simulation_input)
    deployinst_dict = convert_xml_to_dict(deployinst_input)

    # get information out of dictionaries
    duration = get_simulation_duration(simulation_dict)
    lwr_powers = get_pris_powers('UNITED STATES OF AMERICA', 2020)
    deployed_lwr_dict = get_deployinst_dict(deployinst_input, lwr_powers, prototype_path)

    # Figure out power already deployed and power needed
    time, deployed_power = get_deployed_power(
        lwr_powers, deployed_lwr_dict, duration)
    demand_eq = np.zeros(len(time))
    demand_eq[721:] = 89450
    power_gap = determine_power_gap(deployed_power, demand_eq)

    # Figure out how many new prototypes are needed
    deploy_schedule = determine_deployment_schedule(
        power_gap, reactor_prototypes)
    write_deployinst(deploy_schedule, output_path)
