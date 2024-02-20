import d3ploy.tester as tester
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
from textwrap import wrap
import seaborn as sns


def format_agent_dict(output_file, simple=True):
    """
    This function takes the agent entry table from the transition scenario
    sqlite file and creates a time series dictionary of the entry the various
    facilities in the simulation. The output of this function is used as an
    input for the plot_agents function to generate nice deployment plots.

    Parameters
    ----------
    output_file : str
        sqlite file name
    simple : boolean.
        True: EG01-23, EG01-24
        False: EG01-29, EG01-30

    Returns
    -------
    agent_dict : dict
        Time series dictionary of the entry the various
        facilities in the simulation.
    """

    if simple:
        in_agent = ['lwr1',
                    'lwr2',
                    'lwr3',
                    'lwr4',
                    'lwr5',
                    'lwr6',
                    'lwr7',
                    'lwr8',
                    'lwr9',
                    'lwr10',
                    'enrichment',
                    'source',
                    'lwrstorage',
                    'lwrreprocessing',
                    'lwrmixer',
                    'lwrsink',
                    'fr',
                    'frstorage',
                    'frreprocessing',
                    'frsink']
    else:
        in_agent = ['lwr1',
                    'lwr2',
                    'lwr3',
                    'lwr4',
                    'lwr5',
                    'lwr6',
                    'lwr7',
                    'lwr8',
                    'lwr9',
                    'lwr10',
                    'enrichment',
                    'source',
                    'lwrstorage',
                    'lwrreprocessing',
                    'lwrmixer',
                    'lwrsink',
                    'moxlwr',
                    'moxmixer',
                    'frmixer',
                    'fr',
                    'moxstorage',
                    'frstorage',
                    'moxreprocessing',
                    'frreprocessing',
                    'frsink',
                    'moxsink']
    agent_dict = tester.get_agent_dict(output_file, in_agent)
    if simple:
        prototypes = ['source',
                      'enrichment',
                      'lwr',
                      'lwrstorage',
                      'lwrreprocessing',
                      'lwrmixer',
                      'lwrsink',
                      'fr',
                      'frstorage',
                      'frreprocessing',
                      'frsink']
    else:
        prototypes = ['enrichment',
                      'source',
                      'lwrstorage',
                      'lwrreprocessing',
                      'lwrmixer',
                      'lwrsink',
                      'moxlwr',
                      'moxmixer',
                      'frmixer',
                      'fr',
                      'moxstorage',
                      'frstorage',
                      'moxreprocessing',
                      'frreprocessing',
                      'frsink',
                      'moxsink']
    agent_dict['lwr'] = {}
    for x in range(10):
        name = 'lwr' + str(x + 1)
        if x == 0:
            agent_dict['lwr'] = Counter(agent_dict[name].copy())
        else:
            agent_dict['lwr'] += Counter(agent_dict[name])
        del agent_dict[name]
    t = list(agent_dict[prototypes[0]].keys())
    prototypes.reverse()
    for x in prototypes:
        if len(agent_dict[x]) < len(agent_dict[prototypes[0]]):
            for key in agent_dict[prototypes[0]]:
                if agent_dict[x].get(key) is None:
                    agent_dict[x][key] = 0
    return agent_dict


def plot_agents(all_agents, name, simple=True):
    """
    This function takes the time series facility entry dictionary output
    from the format_agent_dict function to generate two deployment plots:
    reactors and supporting fuel cycle facilities.

    Parameters
    ----------
    agent_dict : dict
        Time series dictionary of the entry the various
        facilities in the simulation.
    simple : boolean.
        True: EG01-23, EG01-24
        False: EG01-29, EG01-30

    Returns
    -------
    Two plots (reactor and supporting fuel cycle facility plots).
    """
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.grid(alpha=0.7)
    ax.set_xlim(0, 1450)
    ax.set_xlabel('Months', fontsize=18)
    ax.set_ylabel('Number of Agents in Simulation', fontsize=18)
    if simple:
        ax.stackplot(all_agents['lwr'].keys(),
                     all_agents['lwr'].values(),
                     all_agents['fr'].values())
        ax.legend(['lwr', 'sfr'], bbox_to_anchor=(0.15, 1), fontsize=14)
    else:
        ax.stackplot(all_agents['lwr'].keys(),
                     all_agents['lwr'].values(),
                     all_agents['fr'].values(),
                     all_agents['moxlwr'].values())
        ax.legend(['lwr', 'sfr', 'moxlwr'],
                  bbox_to_anchor=(0.15, 1), fontsize=14)
    ax.set_title(
        'No. of Reactor Facilities in simulation at each time step',
        fontsize=18)
    plt.savefig(name + '_reactor', dpi=300, bbox_inches='tight')
    plt.show()
    if simple:
        prototypes = ['enrichment',
                      'source',
                      'lwrstorage',
                      'lwrreprocessing',
                      'lwrmixer',
                      'lwrsink',
                      'frstorage',
                      'frreprocessing',
                      'frsink']
        prototypes2 = ['lwr fuel fabrication plant',
                       'natural uranium source',
                       'lwr fuel cooling pool',
                       'lwr fuel reprocessing plant',
                       'fr fuel fabrication plant',
                       'lwr reprocessing waste',
                       'fr fuel cooling pool',
                       'fr fuel reprocessing plant',
                       'fr reprocessing waste']
    else:
        prototypes = ['enrichment',
                      'source',
                      'lwrstorage',
                      'lwrreprocessing',
                      'lwrsink',
                      'frmixer',
                      'moxmixer',
                      'frreprocessing',
                      'moxreprocessing',
                      'frstorage',
                      'moxstorage',
                      'frsink',
                      'moxsink']
        prototypes2 = ['lwr fuel fabrication plant',
                       'natural uranium source',
                       'lwr fuel cooling pool',
                       'lwr fuel reprocessing plant',
                       'lwr reprocessing waste',
                       'fr fuel fabrication plant',
                       'mox fuel fabrication plant',
                       'fr fuel reprocessing plant',
                       'mox fuel reprocessing plant',
                       'fr fuel cooling pool',
                       'mox fuel cooling pool',
                       'fr reprocessing waste',
                       'mox reprocessing waste']
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.grid(alpha=0.7)
    ax.set_xlim(0, 1450)
    ax.set_xlabel('Months', fontsize=18)
    col = sns.color_palette("tab20", 13)
    ax.set_ylabel('Number of Agents in Simulation', fontsize=18)
    if simple:
        ax.stackplot(all_agents[prototypes[0]].keys(),
                     all_agents[prototypes[0]].values(),
                     all_agents[prototypes[1]].values(),
                     all_agents[prototypes[2]].values(),
                     all_agents[prototypes[3]].values(),
                     all_agents[prototypes[4]].values(),
                     all_agents[prototypes[5]].values(),
                     all_agents[prototypes[6]].values(),
                     all_agents[prototypes[7]].values(),
                     all_agents[prototypes[8]].values(),)
    else:
        ax.stackplot(all_agents[prototypes[0]].keys(),
                     all_agents[prototypes[0]].values(),
                     all_agents[prototypes[1]].values(),
                     all_agents[prototypes[2]].values(),
                     all_agents[prototypes[3]].values(),
                     all_agents[prototypes[4]].values(),
                     all_agents[prototypes[5]].values(),
                     all_agents[prototypes[6]].values(),
                     all_agents[prototypes[7]].values(),
                     all_agents[prototypes[8]].values(),
                     all_agents[prototypes[9]].values(),
                     all_agents[prototypes[10]].values(),
                     all_agents[prototypes[11]].values(),
                     all_agents[prototypes[12]].values(), colors=col)
    ax.legend(prototypes2, bbox_to_anchor=(0.32, 1), fontsize=14)
    ax.set_title(
        'No. of Supporting Facilities in simulation at each timestep',
        fontsize=18)
    plt.savefig(name + '_support', dpi=300, bbox_inches='tight')
    plt.show()


def supplydemanddiff(all_dict):
    """
    This function calculates the difference between supply and
    demand from all_dict.

    Parameters
    ----------
    all_dict : dict
        Dictionary with supply and demand timeseries
        data for a commodity.

    Returns
    -------
    diff_dict : dict
        Dictionary with timeseries data of the difference
        between supply and demand.
    """

    dict_demand = all_dict['dict_demand']
    dict_supply = all_dict['dict_supply']
    diff_dict = {}
    for key in dict_demand:
        diff_dict[key] = dict_supply[key] - dict_demand[key]
    return diff_dict


def get_undersupply_timesteps(
        output_file,
        commod,
        driving_commod=False,
        demand_eq='0',
        demand_driving=True):
    """
    Returns timeseries dictionaries for existence of undersupply of a commodity
    and the absolute value of this undersupply.

    Parameters
    ----------
    output_file : str
        Path to the SQLite file.
    commod : str
        Name of the commodity.
    driving_commod : bool, optional
        Indicates if the commodity is a driving commodity (True) or not (False).
        Defaults to False.
    demand_eq : str, optional
        Demand equation, only used if driving_commod is True.
        Defaults to '0'.
    demand_driving : bool, optional
        Indicates whether the commodities are demand-driven (True) or supply-driven (False).
        Defaults to True.

    Returns
    -------
    dict_dots : dict
        Timeseries dictionary with 1 and 0 indicating undersupply at specific time steps.
    diff_dict_drop : dict
        Timeseries dictionary with absolute difference between supply and demand, if supply < demand.
    """

    if driving_commod:
        all_dict = tester.supply_demand_dict_driving(
            output_file, demand_eq, commod)
    else:
        if demand_driving:
            all_dict = tester.supply_demand_dict_nondriving(
                output_file, commod, True, calc=False)
        else:
            all_dict = tester.supply_demand_dict_nondriving(
                output_file, commod, False, calc=False)
    diff_dict = supplydemanddiff(all_dict)
    dict_dots = {}
    diff_dict_drop = {}
    for key in diff_dict:
        if demand_driving:
            if diff_dict[key] < 0:
                dict_dots[key] = 1
                diff_dict_drop[key] = diff_dict[key]

        else:
            if diff_dict[key] > 0:
                dict_dots[key] = 1
                diff_dict_drop[key] = diff_dict[key]
    return dict_dots, diff_dict_drop


def plot_all_undersupply(
        commods,
        commodnames,
        methods,
        general_sqlite,
        demand_driven=True,
        demand_eq='0',
        title='',
        name='hello'):
    """
    Generates a comparison plot of commodity undersupply for different prediction methods.

    Parameters
    ----------
    commods : list of str
        List of commodities.
    commodnames : list of str
        List of commodity names to display on the y-axis of the plot.
    methods : list of str
        List of prediction methods.
    general_sqlite : str
        Name of the SQLite database without the method name added at the end.
    demand_driven : bool, optional
        Boolean indicating whether the commodities are demand-driven (True) or supply-driven (False).
        Defaults to True.
    demand_eq : str, optional
        Equation for power demand. Defaults to '0'.
    title : str, optional
        Title of the plot. Defaults to an empty string.
    name : str, optional
        Name of the PNG file for the figure. Defaults to an empty string.

    Returns
    -------
    None :
        Saves plots named according to the name argument.
    """

    num = len(commods) * 1.5
    fig, (ax, ax1) = plt.subplots(
        1, 2, sharey=True, facecolor='w', figsize=(15, num))
    ax.set_xlim(0, 100)
    ax1.set_xlim(900, 1450)
    ax.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax.yaxis.tick_left()
    ax.tick_params(labelright='off')
    ax1.yaxis.tick_right()

    NUM_COLORS = 10
    cm = plt.get_cmap("tab10")
    colors = [cm(1.0 * i / NUM_COLORS) for i in range(NUM_COLORS)]
    for y in range(len(methods)):
        output_file = general_sqlite + methods[y] + '.sqlite'
        for x in range(len(commods)):
            if commods[x] == 'power':
                dots, diff = get_undersupply_timesteps(
                    output_file, commods[x], demand_eq=demand_eq,
                    driving_commod=True)
            elif demand_driven:
                dots, diff = get_undersupply_timesteps(output_file, commods[x])
            else:
                dots, diff = get_undersupply_timesteps(
                    output_file, commods[x], demand_driving=False)
            for key in dots:
                dots[key] *= (x + 0.1 + 0.1 * y)
            a = list(diff.values())
            a = [abs(x) for x in a]
            size = [abs(round(elem / max(a) * 300)) for elem in a]
            if x == 0:
                ax.scatter(
                    dots.keys(),
                    dots.values(),
                    color=colors[y],
                    s=size,
                    label=methods[y],
                    marker='x')
                ax1.scatter(
                    dots.keys(),
                    dots.values(),
                    color=colors[y],
                    s=size,
                    label=methods[y],
                    marker='x')
            else:
                ax.scatter(
                    dots.keys(),
                    dots.values(),
                    color=colors[y],
                    s=size,
                    marker='x')
                ax1.scatter(
                    dots.keys(),
                    dots.values(),
                    color=colors[y],
                    s=size,
                    marker='x')

    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass plot, just so we don't keep repeating them
    kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
    ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)
    ax.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

    kwargs.update(transform=ax1.transAxes)  # switch to the bottom axes
    ax1.plot((-d, +d), (1 - d, 1 + d), **kwargs)
    ax1.plot((-d, +d), (-d, +d), **kwargs)
    ax.set_ylim(0, len(commods))
    ax.set_yticks(np.arange(0, len(commods)))
    commodnames = ['\n'.join(wrap(l, 9)) for l in commodnames]
    ax.set_yticklabels(commodnames)
    ax.grid(alpha=0.7)
    ax1.grid(alpha=0.7)
    plt.axvspan(961, 1141, color='gray', alpha=0.1, label='Transition Period')
    ax1.legend(bbox_to_anchor=(1.5, 1), fontsize=14)
    fig.text(0.5, 0.01, 'Time Steps (Months)', fontsize=18, ha='center')
    ax.set_ylabel('Commodities', fontsize=18)
    plt.suptitle(title, fontsize=18)
    plt.savefig(name, dpi=300, bbox_inches='tight')
    plt.show()


def histogram_formatting(
        commods,
        methods,
        general_sqlite,
        demand_driven=True,
        demand_eq='0'):
    """
    Formats data for generating histograms of undersupplied time steps.

    Parameters
    ----------
    commods : list
        List of commodities.
    methods : list
        List of prediction methods.
    general_sqlite : str
        General SQLite database filename path.
    demand_driven : bool, optional
        Flag indicating if demand-driven mode is enabled (default is True).
    demand_eq : str, optional
        Equation for demand (default is '0').

    Returns
    -------
    dict
        A dictionary containing formatted data for generating histograms.
        The keys are prediction methods, and the values are dictionaries
        where the keys are commodities and the values are arrays representing
        histogram bin values.
    """
    everything = {}
    for y in methods:
        everything[y] = {}
    for y in range(len(methods)):
        output_file = general_sqlite + methods[y] + '.sqlite'
        for x in range(len(commods)):
            if commods[x] == 'power':
                dots, diff = get_undersupply_timesteps(
                    output_file, commods[x], demand_eq=demand_eq,
                    driving_commod=True)
            elif demand_driven:
                dots, diff = get_undersupply_timesteps(output_file, commods[x])
            else:
                dots, diff = get_undersupply_timesteps(
                    output_file, commods[x], demand_driving=False)
            binvals, binsize = np.histogram(
                list(
                    dots.keys()), bins=list(np.arange(0, 1450, 50)))
            everything[methods[y]][commods[x]] = binvals
    return everything


def plot_histogram(
        commods1,
        commodnames1,
        commods2,
        commodnames2,
        methods,
        methodnames,
        general_sqlite,
        demand_eq,
        title,
        name,
        yticks):
    """
    Plots a histogram comparing undersupplied time steps for different commodities and prediction methods.

    Parameters
    ----------
    commods1 : list
        List of commodities for dataset 1.
    commodnames1 : list
        Names of commodities for dataset 1.
    commods2 : list
        List of commodities for dataset 2.
    commodnames2 : list
        Names of commodities for dataset 2.
    methods : list
        List of prediction methods.
    methodnames : list
        Names of prediction methods.
    general_sqlite : object
        Object for handling SQLite database.
    demand_eq : bool
        Boolean indicating whether demand-driven mode is enabled.
    title : str
        Title for the histogram plot.
    name : str
        Name of the file to save the plot.
    yticks : list
        List of values for y-axis ticks.

    Returns
    -------
    None
    """
    everything1 = histogram_formatting(
        commods=commods1,
        methods=methods,
        general_sqlite=general_sqlite,
        demand_driven=True,
        demand_eq=demand_eq)
    everything2 = histogram_formatting(
        commods=commods2,
        methods=methods,
        general_sqlite=general_sqlite,
        demand_driven=False,
        demand_eq=demand_eq)
    everything = everything1.copy()
    for x in methods:
        everything[x].update(everything2[x])
    commods = commods1 + commods2
    commodnames = commodnames1 + commodnames2
    fig = plt.figure(figsize=(15, 15))
    palette = plt.get_cmap('Paired')
    for y in range(len(methods)):
        ax = fig.add_subplot(4, 2, y + 1)
        ind = np.arange(28)
        totalbottom = 0
        for x in range(len(everything[methods[y]])):
            if x == 0:
                ax.bar(ind + 0.5, everything[methods[y]]
                       [commods[x]], color=palette(x))
            else:
                ax.bar(ind + 0.5,
                       everything[methods[y]][commods[x]],
                       bottom=totalbottom,
                       color=palette(x))
            totalbottom += everything[methods[y]][commods[x]]
        ax.set_title('Prediction Method: ' + methodnames[y])
        ax.set_ylabel('Undersupplied time steps', fontsize=14)
        ax.set_xlabel('Month', fontsize=14)
        ax.set_xticks(ind)
        months = list(np.arange(0, 1450, 50))
        ax.set_xticklabels(months, rotation=65)
        ax.set_yticks(yticks)
        ax.set_ylim(0, yticks[-1])
        ax.yaxis.grid()
        if y == len(methods) - 1:
            ax.legend(commodnames, loc="upper center",
                      ncol=4, bbox_to_anchor=(-0.07, -0.3))
    fig.subplots_adjust(
        left=None,
        bottom=None,
        right=None,
        top=None,
        wspace=None,
        hspace=0.4)
    fig.subplots_adjust(bottom=-0.1, wspace=0.15)
    props = dict(boxstyle='round', facecolor='white', alpha=0.5)
    fig.suptitle(title, x=0.50, y=0.92, fontsize=16)
    plt.savefig(name, dpi=400, bbox_inches='tight')
    return
