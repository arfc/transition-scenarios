"""
This script creates a .png file that compares the cumulative undersupply
for different calculation methods and different buffer sizes.
It can also plot for differnet no. of forward/back steps.
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

ENV = dict(os.environ)
ENV['PYTHONPATH'] = ".:" + ENV.get('PYTHONPATH', '')

calc_methods = ['ma', 'arma', 'arch', 'poly', 'exp_smoothing',
                'holt_winters', 'fft']

demand_eq = "60000"

name = 'eg01-eg29-flatpower-d3ploy-buffer'

metric_dict = {}
all_dict = {}
cumulative_under = {}
timesteps_under = {}

# add_list contains the buffer sizes
add_list = ['0', '2000', '4000', '6000', '8000']

for calc_method in calc_methods:

    cumulative_under[calc_method] = {}
    timesteps_under[calc_method] = {}

    for add in add_list:
        output_file = name + add + '-' + calc_method + '.sqlite'

        all_dict['power'] = tester.supply_demand_dict_driving(output_file,
                                                              demand_eq,
                                                              'power')
        metric_dict = tester.metrics(all_dict['power'], metric_dict,
                                     calc_method, 'power', True)

        cumulative_under[calc_method][add] = \
            metric_dict['power_cumulative_undersupply'][calc_method]
        timesteps_under[calc_method][add] = \
            metric_dict['power_undersupply'][calc_method]

plot_buff('29-sens-buffer', calc_methods, add_list, cumulative_under, 'buffer')

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
        metric_dict = tester.metrics(all_dict['power'], metric_dict,
                                     calc_method, 'power', True)

        cumulative_under[calc_method][add] = \
            metric_dict['power_cumulative_undersupply'][calc_method]
        timesteps_under[calc_method][add] = \
            metric_dict['power_undersupply'][calc_method]

plot_buff('29-sens-steps', calc_methods, add_list, cumulative_under, 'steps')
