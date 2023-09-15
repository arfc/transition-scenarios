import numpy as np
import pandas as pd
import xmltodict
from pprint import pprint
import math
import os


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


def get_deployinst_dict(
        deployinst_dict,
        power_dict,
        path="../input/haleu/inputs/united_states/reactors/"):
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
        and optionally 'lifetimes'. Each of those rx_info  dictionaries are
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
                deployed_dict['lifetime'].append(int(
                    deployinst_dict['DeployInst']['lifetimes']['val'][indx]))
            else:
                deployed_dict['lifetime'].append(get_lifetime(path, val))
            deployed_dict['prototypes'].append(val)
            deployed_dict['n_build'].append(
                int(deployinst_dict['DeployInst']['n_build']['val'][indx]))
            deployed_dict['build_times'].append(
                int(deployinst_dict['DeployInst']['build_times']['val'][indx]))
    return deployed_dict


def get_powers(path):
    '''
    Read through each of the xml files in a given path to get the power
    output of each reactor facility. Getting this information from these
    files accounts for any capacity factors, which are not captured in
    the PRIS database. Assumes that all xml files in the specified
    directory are for a Cycamore reactor.

    Parameters:
    -----------
    path: str
        directory name containing xml files for reactors

    Returns:
    --------
    reactor_power: dict
        dictionary of reactor names and rated powers, the keys are the reactor
        names (strs), the values are their power outputs (ints). Any spaces
        in the keys are replaced with underscores.
    '''
    reactor_power = {}
    for filename in os.listdir(path):
        file = os.path.join(path, filename)
        if file[-4:] != ".xml":
            continue
        reactor_info = convert_xml_to_dict(file)

        reactor_power.update(
            {filename[:-4]: reactor_info['facility']['config']['Reactor']['power_cap']
             }
        )
    return reactor_power

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
            prototype_power[deployed_dict['build_times'][i]:deployed_dict['build_times'][
                i] + deployed_dict['lifetime'][i]] += \
                float(power_dict[v] * deployed_dict['n_build'][i])
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


def update_di(di, prototype, num_reactors, build_time, lifetime):
    '''
    Update a dictionary of a DeployInst

    Parameters:
    -----------
    di: dictionary
        dictionary defining the DeployInst, the top-level key
        is 'DeployInst', the next level keys are 'prototypes',
        'n_build', 'lifetimes', and 'build_times'. Each of the
        second level keys have a nested dictionary of
        'val':list
    prototype: str
        name of prototype to be deployed
    num_reactors: int
        number of prototypes to be deployed
    build_time: int
        time step to deploy the prototype
    lifetime: int
        lifetime of the prototype

    Returns:
    --------
    di: dictionary
        updated dictionary to define the DeployInst
    '''
    di['DeployInst']['prototypes']['val'].append(prototype)
    di['DeployInst']['n_build']['val'].append(num_reactors)
    di['DeployInst']['build_times']['val'].append(build_time)
    di['DeployInst']['lifetimes']['val'].append(lifetime)

    return di


def update_power_demand(
        power_gap,
        index,
        power,
        num_reactors,
        reactor_prototypes,
        prototype):
    '''
    Subtracts power from the total demand to be filled
    based on the number of reactors to be deployed

    Parameters:
    power_gap: list or array
        demand in power to be filled
    index: int
        time step, index, of power_gap to start from
    power: float
        value from the power_gap at the index position
    num_reactors: int
        number of reactors of a given prototype to deploy
    reactor_prototypes: dict
        keys are the names of the prototypes, the values are a
        tuple of the power output and lifetime of the
        prototype
    prototype: str
        name of prototype to be deployed

    Returns:
    --------
    power_gap: array
        updated values for the power demand after the deployment
        of a given number of a specified prototype
    power: float
        updated value of power_gap for the index position after
        the deployment of a given number of a specified
        prototype
    '''
    reactor = reactor_prototypes[prototype]
    power_gap[index:index + reactor[1]] -= reactor[0] * num_reactors
    power -= reactor[0] * num_reactors
    return power_gap, power


def deploy_with_share(reactor_prototypes, shares, power, reactor):
    '''
    Deploy prototypes with a defined build share for some or all prototypes

    Parameters:
    -----------
    reactor_prototypes: dict
        information about prototypes,
        {name(str):(power(float),lifetime(int))}
    shares: dict
        contains information about build share for specified
        prototypes, {name(str):build share(int)}
    power: float
        amount of power that needs to be deployed at a given time step.
    prototype: str
        name of prototype to be deployed

    Returns:
    --------
    num_reactors: int
        number of the specified prototype to be deployed at a given time
        step
    '''
    required_share = power * (shares[reactor] / 100)
    num_reactors = math.ceil(
        required_share /
        reactor_prototypes[reactor][0])
    if num_reactors < 0:
        num_reactors = 0

    return num_reactors


def deploy_without_share(prototype, reactors, reactor_prototypes, power):
    '''
    Deploy reactors when a build share isn't supplied for the prototype

    Parameters:
    -----------
    prototype: str
        name of prototype to be deployed
    reactors: list of strs
        list of all prototypes that don't have a specified build share,
        the order of prototypes is in descending order of power output
    reactor_prototypes: dict
        information about prototypes,
        {name(str):(power(float),lifetime(int))}
    power: float
        amount of power that needs to be deployed at a given time step

    Returns:
    --------
    num_reactors: int
        number of the specified prototype to be deployed at a given time
        step
    '''
    reactor_power = reactor_prototypes[prototype][0]
    if prototype == reactors[-1]:
        num_reactors = math.ceil(power / reactor_power)
    else:
        num_reactors = math.floor(power / reactor_power)
    if num_reactors < 0:
        num_reactors = 0

    return num_reactors


def redeploy_reactors(
        power,
        prototype,
        reactor_prototypes,
        deploy_schedule,
        item):
    '''
    Determines the number of advanced reactors to be redeployed. This function
    initially assumes that the number of reactors decommissioning at a
    given time step (the current timestep minus the lifetime of the
    prototype) are to be redeployed. Then the function determines the
    number of prototypes needed to fill the current gap in energy demand.
    If this calculated number is lower than the number initially deployed,
    then the calculated number of the prototype is deployed.

    The logic behind this function is to maintain a relatively constant
    number of each prototype deployed while also minimizing the
    oversupply of energy and minimizing the number of reactors deployed.

    Parameters:
    -----------
    power: float
        gap between energy demand and production at a given time step
    prototype: str
        name of prototype to be deployed
    reactor_prototypes: dict
        information about prototypes,
        {name(str):(power(float),lifetime(int))}
    deploy_schedule: dict
        deployment schedule of reactor prototypes with the
        structure for a DeployInst
    item: int
        index of deploy_schedule['DeployInst']['build_times'] in which
        prototype was deployed at timestep current minus prototype lifetime

    Returns:
    --------
    num_reactors: int
        number of a prototype to deploy
    '''
    num_reactors = deploy_schedule['DeployInst']['n_build']['val'][item]
    reactor_power = reactor_prototypes[prototype][0]
    decreased_deployment = math.ceil(power / reactor_power)
    if decreased_deployment < num_reactors:
        num_reactors = decreased_deployment
    if num_reactors < 0:
        num_reactors = 0

    return num_reactors


def determine_deployment_schedule(
        power_gap,
        reactor_prototypes,
        shares=None):
    '''
    Define the deployment schedule for one or more
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
    shares: dict
        contains information about build share for specified
        prototypes, {name(str): build share(int)}

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
    deployment_order = determine_deployment_order(reactor_prototypes)
    non_shares = deployment_order.copy()
    if shares:
        for reactor in shares:
            non_shares.remove(reactor)
    for index, value in enumerate(power_gap):
        if value <= 0:
            continue
        # redeploy reactors
        num_reactors = {
            k: v for k, v in zip(
                deployment_order, np.repeat(
                    0, len(deployment_order)))}
        for reactor in deployment_order:
            previous_time = index - reactor_prototypes[reactor][1]
            if previous_time in deploy_schedule['DeployInst']['build_times']['val']:
                previous_index = [
                    ii for ii, e in enumerate(
                        deploy_schedule['DeployInst']['build_times']['val']) if
                    e == previous_time]
                for item in previous_index:
                    if deploy_schedule['DeployInst']['prototypes']['val'][item] == reactor:
                        new_reactors = redeploy_reactors(value,
                                                         reactor,
                                                         reactor_prototypes,
                                                         deploy_schedule,
                                                         item)
                        power_gap, value = update_power_demand(
                            power_gap, index, value, new_reactors, reactor_prototypes, reactor)
                        num_reactors[reactor] += new_reactors
        # Deploy new reactors
        if shares:
            for reactor in shares:
                new_reactors = deploy_with_share(
                    reactor_prototypes, shares, value, reactor)
                power_gap, value = update_power_demand(
                    power_gap, index, value, new_reactors, reactor_prototypes, reactor)
                num_reactors[reactor] += new_reactors
        for reactor in non_shares:
            new_reactors = deploy_without_share(
                reactor, non_shares, reactor_prototypes, value)
            power_gap, value = update_power_demand(
                power_gap, index, value, new_reactors, reactor_prototypes, reactor)
            num_reactors[reactor] += new_reactors
        for reactor in deployment_order:
            if num_reactors[reactor] <= 0:
                continue
            deploy_schedule = update_di(
                deploy_schedule,
                reactor,
                num_reactors[reactor],
                index,
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


def write_lwr_deployinst(lwr_param, DI_file, lwr_order):
    '''
    Create a DeployInst for the LWRs in the simulation using different
    lifetimes than what is defined from creating the DeployInst via
    scripts/create_cyclus_input.py. The first agent in the DeployInst
    is the SinkHLW, leading to the first lifetime item being 600
    time steps.

    Parameters:
    -----------
    lwr_param: float
        percent of LWRs to receive lifetime extensions
    DI_file: str
        file name and path to DeployInst file for LWRs to base information
        off of.
    lwr_order: str
        path and name of file containing LWRs ordered by power output.

    Returns:
    --------
    DI_dict: dict
        nested dictionary, contains information for the DeployInst in
        the form {'DeployInst':{'prototypes':{'val':[]}, 'n_build':
        {'val':[]}, 'build_times':{'val':[]},'lifetimes':{'val':[]}}}.
        The values in the inner-most dict are ints
    '''
    DI_dict = convert_xml_to_dict(DI_file)
    DI_dict['DeployInst']['lifetimes'] = {'val': []}
    DI_dict['DeployInst']['lifetimes']['val'] = np.repeat(720, 116)
    DI_dict['DeployInst']['lifetimes']['val'][0] = 600

    with open(lwr_order, 'r') as f:
        lwrs = f.readlines()
    for index, item in enumerate(lwrs):
        lwrs[index] = item.strip("\n")
    lwrs_extended = lwrs[:int(lwr_param) + 1]

    for lwr in lwrs_extended:
        index = DI_dict['DeployInst']['prototypes']['val'].index(lwr)
        DI_dict['DeployInst']['lifetimes']['val'][index] = 960
    return DI_dict


def write_AR_deployinst(
        lwr_DI,
        lwr_path,
        duration,
        reactor_prototypes,
        demand_eq,
        shares=None):
    ''''
    Creates the DeployInst for the deployment of advanced reactors

    Parameters:
    -----------
    lwr_DI: dict
        dictionary of the DeployInst defining the deployment of LWRs
    lwr_path: str
        path to directory containing xml files defining each LWR in
        the simulation
    duration: int
        number of time steps in the simulation
    reactor_prototypes: dict
        dictionary of information about prototypes in the form
        {name(str):(power(int),lifetime(int))}
    demand_eq: array
        energy demand at each time step in the simulation, length
        must match the value of duration
    shares: dict
        contains information about build share for specified
        prototypes, {name(str):build share(int)}


    Returns:
    --------
    deploy_schedule: dict
        nested dictionary, contains information for the DeployInst in
        the form {'DeployInst':{'prototypes':{'val':[]}, 'n_build':
        {'val':[]}, 'build_times':{'val':[]},'lifetimes':{'val':[]}}}.
        The values in the inner-most dict are ints
    '''
    lwr_powers = get_powers(lwr_path)
    deployed_lwr_dict = get_deployinst_dict(
        lwr_DI, lwr_powers, lwr_path)
    time, deployed_power = get_deployed_power(lwr_powers,
                                              deployed_lwr_dict,
                                              duration)
    power_gap = determine_power_gap(deployed_power, demand_eq)
    deploy_schedule = determine_deployment_schedule(power_gap,
                                                    reactor_prototypes,
                                                    shares)
    return deploy_schedule
