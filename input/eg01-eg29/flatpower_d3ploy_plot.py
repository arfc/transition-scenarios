"""
This script creates the .csv file and the .png files for power
asociated to a scenario run with multiple calculations methods.
It produces one .png for NO, one for DO, and one for SO.
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


def plot_several(name, all_dict, commod, calc_methods, demand_eq):
    dict_demand = {}
    dict_supply = {}

    for calc_method in calc_methods:
        dict_demand[calc_method] = all_dict[calc_method]['dict_demand']
        dict_supply[calc_method] = all_dict[calc_method]['dict_supply']

    fig, ax = plt.subplots(figsize=(15, 7))

    ax.semilogy(*zip(*sorted(dict_demand[calc_method].items())), '-',
                color='red', label='Demand')

    for calc_method in calc_methods:
        ax.semilogy(*zip(*sorted(dict_supply[calc_method].items())), 'x',
                    label=calc_method + ' Supply', markersize=4)

    ax.set_xlabel('Time (month timestep)', fontsize=21)
    if commod.lower() == 'power':
        ax.set_ylabel('Power (MW)', fontsize=21)
    else:
        ax.set_ylabel('Mass (Kg)', fontsize=21)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, fontsize=18, loc='upper center',
              bbox_to_anchor=(1.1, 1.0), fancybox=True)

    # plt.minorticks_off()
    # ax.set_yticks(np.arange(5.8e4, 6.5e4, 2.e3))
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

front_commods = ['sourceout', 'enrichmentout', 'frmixerout', 'moxmixerout']
back_commods = ['lwrstorageout', 'frstorageout', 'moxstorageout']

buffer_size = '0'
name = 'eg01-eg29-flatpower-d3ploy' + buffer_size


for calc_method in calc_methods:
    output_file = name + '-' + calc_method + '.sqlite'

    all_dict['power'] = tester.supply_demand_dict_driving(output_file,
                                                          demand_eq,
                                                          'power')

    metric_dict = tester.metrics(
        all_dict['power'], metric_dict, calc_method, 'power', True)

    for commod in front_commods:
        all_dict[commod] = tester.supply_demand_dict_nondriving(output_file,
                                                                commod, True)
        metric_dict = tester.metrics(
            all_dict[commod], metric_dict, calc_method, commod, True)

    for commod in back_commods:
        all_dict[commod] = tester.supply_demand_dict_nondriving(output_file,
                                                                commod, False)
        metric_dict = tester.metrics(
            all_dict[commod], metric_dict, calc_method, commod, False)

    df = pd.DataFrame(metric_dict)
    df.to_csv(name + '.csv')

calc_methods1 = ["ma", "arma", "arch"]
calc_methods2 = ["poly", "exp_smoothing", "holt_winters", "fft"]
calc_methods3 = ["sw_seasonal"]

for calc_method in calc_methods1:
    output_file = name + '-' + calc_method + '.sqlite'
    all_dict[calc_method] = tester.supply_demand_dict_driving(output_file,
                                                              demand_eq,
                                                              'power')

plot_several('29-power' + buffer_size + '1', all_dict, 'power', calc_methods1,
             demand_eq)
for calc_method in calc_methods2:
    output_file = name + '-' + calc_method + '.sqlite'
    all_dict[calc_method] = tester.supply_demand_dict_driving(output_file,
                                                              demand_eq,
                                                              'power')

plot_several('29-power' + buffer_size + '2', all_dict, 'power', calc_methods2,
             demand_eq)

for calc_method in calc_methods3:
    output_file = name + '-' + calc_method + '.sqlite'
    all_dict[calc_method] = tester.supply_demand_dict_driving(output_file,
                                                              demand_eq,
                                                              'power')

plot_several('29-power' + buffer_size + '3', all_dict, 'power', calc_methods3,
             demand_eq)
