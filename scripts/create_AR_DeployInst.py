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


def get_deployinst_dict(deployinst_dict, power_dict, path="../input/haleu/inputs/united_states/reactors/"):
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
        dictionary of DeployInst information. This dictionary is assumed
        to be nested, with the top key being 'DeployInst', the keys of
        the next level being 'prototypes', 'build_times', 'n_build',
        and optionally 'lifetimes'. Each of thos dictionaries will be
        nested with key of 'val', and value of a list of the integer
        values.
    reactor_dict: dict
        dictionary of LWR prototype names. Keys are the names of each
        prototype for LWRs, with values of the rated power for the prototype.
    path: str
        path to xml files for each prototype

    Returns:
    --------
    deployed_dict: dict
        dictionary of information about LWR prototypes and
        their deployment. The keys are strs and values are lists of
        ints.
    '''
    deployed_dict = {}
    deployed_dict = {'lifetime': [],
                     'prototypes': [],
                     'n_build': [],
                     'build_times': []}
    for indx, val in enumerate(
            deployinst_dict['DeployInst']['prototypes']['val']):
        if val in power_dict.keys():
            if 'lifetimes' in deployinst_dict['DeployInst']:
                deployed_dict['lifetime'].append(int(deployinst_dict['DeployInst']['lifetimes']['val'][indx]))
            else:
                deployed_dict['lifetime'].append(get_lifetime(path, val))
            deployed_dict['prototypes'].append(val)
            deployed_dict['n_build'].append(
                int(deployinst_dict['DeployInst']['n_build']['val'][indx]))
            deployed_dict['build_times'].append(
                int(deployinst_dict['DeployInst']['build_times']['val'][indx]))
    return deployed_dict


def get_pris_powers(country, path, year):
    '''
    Create dictionary of the reactor units from a select country
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
    pris_power = {k.replace(' ', '_'): v for k, v in pris_power.items()}
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
        contains the power output of each agent in the DeployInst.
        The keys are the reactor
        names (strs), the values are the rated powers (ints). Any spaces
        in the keys are replaced with underscores.
    deployed_dict: dict
        contains the lifetimes, number built, and name of each
        prototype in the DeployInst. The keys are strs and values
        are lists of ints.
    sim_duration: int
        number of timesteps in the simulation

    Returns:
    --------
    t: array of ints
        ranged arrays of durations
    inst_power: array of ints
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
    power_profile: array of ints
        Amount of power produced at each time step
    demand: array of ints
        evaluated values of the power demand equation used

    Returns:
    --------
    power_gap: array of ints
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
    Define the deployment schedule for a single or multiple
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
            value = value - reactor_prototypes[reactor][0] * num_rxs
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
        deployment schedule of reactor prototypes, with
        the same schema as the DeployInst. Nest dictionary
        with the top key being 'DeployInst', next level of keys in
        'prototypes', 'n_build', 'build_times',  and 'lifetimes'. Each
        of those keys has a nested dictionary of {'val':[]}, with
        the values of that dictionary being a list.
    out_path: str
        path to where the file should be written

    Returns:
    --------
    null
        wites xml file for Cycamore DeployInst
    '''
    with open(out_path, 'w') as f:
        f.write(xmltodict.unparse(deploy_schedule, pretty=True))
