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


def plot_buff(name, calc_methods, buff_sizes, data, buff=True):
    fig, ax = plt.subplots(figsize=(15, 7))
    for calc_method in calc_methods:
        # Plots markers instead of lines.
        # ax.plot(*zip(*sorted(data[calc_method].items())), 'x',
        #         label=calc_method, markersize=4)
        ax.plot(*zip(*sorted(data[calc_method].items())),
                label=calc_method)
    if buff:
        ax.set_xlabel('Buffer Size [MW]', fontsize=14)
    else:
        ax.set_xlabel('Back Steps', fontsize=14)
    ax.set_ylabel('Cumulative Undersupply [GW]', fontsize=14)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, fontsize=11, loc='upper center',
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

calc_methods = ["ma", "arma", "arch", "poly", "exp_smoothing", "holt_winters",
                "fft", "sw_seasonal"]

demand_eq = "60000"

metric_dict = {}
all_dict = {}
cumulative_under = {}
timesteps_under = {}

name = 'eg01-eg23-flatpower-d3ploy-buffer'

# add_list contains the buffer sizes
# it can be replaced by forward steps/back steps.
add_list = ['0', '2000', '4000']
# add_list = ['1', '3', '5']

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

        cumulative_under[calc_method][add] = metric_dict['power_residuals_under'][calc_method] - 60e3
        timesteps_under[calc_method][add] = metric_dict['power_undersupply'][calc_method] - 1

plot_buff('asave/23-buff', calc_methods, add_list, cumulative_under)
# plot_buff('asave/23-for', calc_methods, add_list, cumulative_under,
#           buff = False)
