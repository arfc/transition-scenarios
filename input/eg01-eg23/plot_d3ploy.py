"""
This file produces the plots for one scenario.
The plots are produced for only one calculation method.
This is not useful to compare different calculation methods
but to see the outputs of only one simulation.
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
import numpy as np
import pandas as pd
import d3ploy.tester as tester
import d3ploy.plotter as plotter
import collections

direc = os.listdir('./')

# Delete previously generated files
# hit_list = glob.glob('*.png') + glob.glob('*.csv')
# for file in hit_list:
#     os.remove(file)

ENV = dict(os.environ)
ENV['PYTHONPATH'] = ".:" + ENV.get('PYTHONPATH', '')

# initialize metric dict
demand_eq = '60000'
calc_method = 'poly'
name = "eg01-eg23-flatpower-d3ploy-buffer0-poly"
output_file = name + ".sqlite"

# Initialize dicts
metric_dict = {}
all_dict = {}
agent_entry_dict = {}

# get agent deployment
commod_dict = {'enrichmentout': ['enrichment'],
               'sourceout': ['source'],
               'power': ['fr', 'lwr1', 'lwr2', 'lwr3', 'lwr4', 'lwr5',
                         'lwr6', 'lwr7', 'lwr8', 'lwr9', 'lwr10'],
               'lwrstorageout': ['lwrreprocessing'],
               'frstorageout': ['frreprocessing'],
               'lwrout': ['lwrstorage'],
               'frout': ['frstorage'],
               'lwrpu': ['lwrmixer'],
               'frpu': ['frmixer'],
               'mixerout': ['fr'],
               'lwrreprocessingwaste': ['lwrsink'],
               'frreprocessingwaste': ['frsink']}

for commod, facility in commod_dict.items():
    agent_entry_dict[commod] = tester.get_agent_dict(output_file, facility)

all_dict['power'] = tester.supply_demand_dict_driving(
    output_file, demand_eq, 'power')

plotter.plot_demand_supply_agent(all_dict['power'], agent_entry_dict['power'],
                                 'power', '0-' + calc_method + '-power',
                                 True, True, False, 1)

front_commods = ['sourceout', 'enrichmentout']
mid_commods = ['mixerout']
back_commods = ['lwrstorageout', 'frstorageout', 'lwrout', 'frout',
                'lwrreprocessingwaste', 'frreprocessingwaste', 'frpu',
                'lwrpu']

for commod in front_commods:
    all_dict[commod] = tester.supply_demand_dict_nondriving(output_file,
                                                            commod, True)
    name = '0-' + calc_method + '-' + commod
    plotter.plot_demand_supply_agent(all_dict[commod],
                                     agent_entry_dict[commod], commod, name,
                                     True, True, False, 1)
    metric_dict = tester.metrics(
        all_dict[commod], metric_dict, calc_method, commod, True)

for commod in mid_commods:
    all_dict[commod] = tester.supply_demand_dict_nond3ploy(output_file,
                                                           commod)
    name = '0-' + calc_method + '-' + commod
    plotter.plot_demand_supply_nond3ploy(all_dict[commod],
                                         agent_entry_dict[commod], commod,
                                         name, True, True, 1)
    metric_dict = tester.metrics(all_dict[commod], metric_dict, calc_method,
                                 commod, False)

for commod in back_commods:
    all_dict[commod] = tester.supply_demand_dict_nondriving(output_file,
                                                            commod, False)

    name = '0-' + calc_method + '-' + commod
    plotter.plot_demand_supply_agent(all_dict[commod],
                                     agent_entry_dict[commod],
                                     commod, name, False, True, False, 1)
    metric_dict = tester.metrics(
        all_dict[commod], metric_dict, calc_method, commod, False)

df = pd.DataFrame(metric_dict)
df.to_csv('0-' + calc_method + '.csv')
