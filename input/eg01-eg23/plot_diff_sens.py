"""
This script creates a .png file that compares the cumulative undersupply
for different buffer sizes, steps, and back steps.

In order to run this script it is necessary to have run previously
the script 'flatpower_d3ploy.py'.
"""

import json
import re
import subprocess
import os
import sqlite3 as lite
import copy
import glob
import sys
from matplotlib import pyplot as plt
import matplotlib
from matplotlib.ticker import ScalarFormatter, NullFormatter
import numpy as np
import pandas as pd
import d3ploy.tester as tester
import d3ploy.plotter as plotter
import collections


def plot_several(name, all_dict, commod, calc_methods, demand_eq, analysis):
    dict_demand = {}
    dict_supply = {}

    for calc_method in calc_methods:
        dict_demand[calc_method] = all_dict[calc_method]['dict_demand']
        dict_supply[calc_method] = all_dict[calc_method]['dict_supply']

    fig, ax = plt.subplots(figsize=(15, 7))

    ax.plot(*zip(*sorted(dict_demand[calc_method].items())), '-',
            color='red', label='Demand')

    for calc_method in calc_methods:
        if analysis == 'buffer':
            ax.plot(*zip(*sorted(dict_supply[calc_method].items())), 'x',
                    label=calc_method + ' Buffer', markersize=3)
        elif analysis == 'steps':
            ax.plot(*zip(*sorted(dict_supply[calc_method].items())), 'x',
                    label=calc_method + ' Steps', markersize=3)
        elif analysis == 'back':
            ax.plot(*zip(*sorted(dict_supply[calc_method].items())), 'x',
                    label=calc_method + ' Back steps', markersize=3)

    ax.set_xlabel('Time (month timestep)', fontsize=21)
    if commod.lower() == 'power':
        ax.set_ylabel('Power (MW)', fontsize=21)
    else:
        ax.set_ylabel('Mass (Kg)', fontsize=21)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, fontsize=20, loc='upper center',
              bbox_to_anchor=(1.1, 1.0), fancybox=True)

    plt.savefig(name, dpi=300, bbox_inches='tight')
    plt.close()


def plot_buff(name, calc_methods, buff_sizes, data, analysis):
    fig, ax = plt.subplots(figsize=(15, 7))
    for calc_method in calc_methods:
        # Plots markers instead of lines.
        # ax.plot(*zip(*sorted(data[calc_method].items())), 'x',
        #         label=calc_method, markersize=4)
        ax.plot(*zip(*sorted(data[calc_method].items())),
                label=calc_method)
    if analysis == 'buffer':
        ax.set_xlabel('Buffer Size [MW]', fontsize=21)
    elif analysis == 'steps':
        ax.set_xlabel('Number of Steps Forward', fontsize=21)
    elif analysis == 'back':
        ax.set_xlabel('Number of Back Steps', fontsize=21)
    ax.set_ylabel('Cumulative Undersupply [GW.mo]', fontsize=21)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, fontsize=20, loc='upper center',
              bbox_to_anchor=(1.1, 1.0), fancybox=True)

    plt.savefig(name, dpi=300, bbox_inches='tight')
    plt.close()


direc = os.listdir('./')

# Delete previously generated files
# hit_list = glob.glob('*.png') + glob.glob('*.csv')
# for file in hit_list:
#     os.remove(file)

ENV = dict(os.environ)
ENV['PYTHONPATH'] = ".:" + ENV.get('PYTHONPATH', '')

calc_methods = ['ma', 'arma', 'arch', 'poly', 'exp_smoothing',
                'holt_winters', 'fft']

demand_eq = "60000"

name = 'eg01-eg23-flatpower-d3ploy-buffer'

# add_list contains the buffer sizes
add_list = ['0', '2000', '4000', '6000', '8000']

metric_dict = {}
all_dict = {}
dic_power = {}
cumulative_under = {}
timesteps_under = {}

for calc_method in calc_methods:

    cumulative_under[calc_method] = {}
    timesteps_under[calc_method] = {}

    for add in add_list:
        output_file = name + add + '-' + calc_method + '.sqlite'
        all_dict['power'] = tester.supply_demand_dict_driving(output_file,
                                                              demand_eq,
                                                              'power')
        dic_power[add] = all_dict['power']
        metric_dict = tester.metrics(all_dict['power'], metric_dict,
                                     calc_method, 'power', True)
        cumulative_under[calc_method][add] = \
            metric_dict['power_cumulative_undersupply'][calc_method]
        timesteps_under[calc_method][add] = \
            metric_dict['power_undersupply'][calc_method]

    # Produces one plot for each calculation method, for several buffer sizes.
    plot_several('23-power-buffer-' + calc_method, dic_power, 'power',
                 add_list, demand_eq, 'buffer')

# Plots cumulative under supply for different buffer sizes for several
# calculation methods.
plot_buff('23-sens-buffer', calc_methods, add_list, cumulative_under, 'buffer')

# choose one buffer size
buff = '0'
# add_list contains the number of steps
add_list = ['1', '2', '3', '4', '5']

for calc_method in calc_methods:

    cumulative_under[calc_method] = {}
    timesteps_under[calc_method] = {}

    for add in add_list:

        output_file = name + buff + '-S' + add + '-' + calc_method + '.sqlite'
        all_dict['power'] = tester.supply_demand_dict_driving(output_file,
                                                              demand_eq,
                                                              'power')
        dic_power[add] = all_dict['power']
        metric_dict = tester.metrics(all_dict['power'], metric_dict,
                                     calc_method, 'power', True)
        cumulative_under[calc_method][add] = \
            metric_dict['power_cumulative_undersupply'][calc_method]
        timesteps_under[calc_method][add] = \
            metric_dict['power_undersupply'][calc_method]

    # Produces one plot for each calculation method, for several
    # steps forward.
    plot_several('23-power-buffer' + buff + '-' + calc_method + '-steps',
                 dic_power, 'power', add_list, demand_eq, 'steps')

# Plots cumulative under supply for different steps forward for several
# calculation methods.
plot_buff('23-sens-steps', calc_methods, add_list, cumulative_under, 'steps')

# choose one buffer size
buff = '0'
# add_list contains the number of back steps
add_list = ['2', '3', '4', '5']

for calc_method in calc_methods:

    cumulative_under[calc_method] = {}
    timesteps_under[calc_method] = {}

    for add in add_list:

        output_file = name + buff + '-B' + add + '-' + calc_method + '.sqlite'

        all_dict['power'] = tester.supply_demand_dict_driving(output_file,
                                                              demand_eq,
                                                              'power')
        dic_power[add] = all_dict['power']
        metric_dict = tester.metrics(all_dict['power'], metric_dict,
                                     calc_method, 'power', True)

        cumulative_under[calc_method][add] = \
            metric_dict['power_cumulative_undersupply'][calc_method]
        timesteps_under[calc_method][add] = \
            metric_dict['power_undersupply'][calc_method]

    # Produces one plot for each calculation method, for several
    # back steps.
    plot_several('23-power-buffer' + buff + '-' + calc_method + '-back',
                 dic_power, 'power', add_list, demand_eq, 'back')

# Plots cumulative under supply for different back steps for several
# calculation methods.
plot_buff('23-sens-backs', calc_methods, add_list, cumulative_under, 'back')
