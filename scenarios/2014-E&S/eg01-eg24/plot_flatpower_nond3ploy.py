# this file produces the plots for the case eg01-eg23-flatpower-d3ploy.xml

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
# hit_list = glob.glob('*.png') + glob.glob('*.csv') + glob.glob('*.txt')
# for file in hit_list:
#     os.remove(file)

ENV = dict(os.environ)
ENV['PYTHONPATH'] = ".:" + ENV.get('PYTHONPATH', '')

# initialize metric dict
demand_eq = '60000'
calc_method = 'ma'
name = "eg01-eg24-flatpower-nond3ploy"
output_file = name + ".sqlite"

# Initialize dicts
metric_dict = {}
all_dict = {}
agent_entry_dict = {}

# get agent deployment
commod_dict = {'enrichmentout': ['enrichment'],
               'sourceout': ['source'],
               'power': ['lwr', 'fr'],
               'lwrstorageout': ['lwrreprocessing'],
               'frstorageout': ['frreprocessing'],
               'lwrout': ['lwrstorage'],
               'frout': ['frstorage'],
               'lwrpu': ['pumixerlwr'],
               'frpu': ['pumixerfr'],
               'lwrreprocessingwaste': ['lwrsink'],
               'frreprocessingwaste': ['frsink']}

for commod, facility in commod_dict.items():
    agent_entry_dict[commod] = tester.get_agent_dict(output_file, facility)

# get supply deamnd dict
all_dict['power'] = tester.supply_demand_dict_nond3ploy(
    output_file, 'power', demand_eq)

plotter.plot_demand_supply_nond3ploy(all_dict['power'],
                                     agent_entry_dict['power'], 'power',
                                     'eg01-eg24-flatpower-nond3ploy_power',
                                     True, True, 1)

front_commods = ['sourceout', 'enrichmentout']
back_commods = ['lwrstorageout', 'frstorageout', 'lwrout', 'frout',
                'lwrreprocessingwaste', 'frreprocessingwaste', 'frpu',
                'lwrpu']

for commod in front_commods:
    all_dict[commod] = tester.supply_demand_dict_nond3ploy(output_file,
                                                           commod)
    name = 'eg01-eg24-flatpower-nond3ploy_' + commod
    plotter.plot_demand_supply_nond3ploy(all_dict[commod],
                                         agent_entry_dict[commod], commod,
                                         name, True, True, 1)

for commod in back_commods:
    all_dict[commod] = tester.supply_demand_dict_nond3ploy(output_file,
                                                           commod, False)

    name = 'eg01-eg24-flatpower-nond3ploy_' + commod
    plotter.plot_demand_supply_nond3ploy(all_dict[commod],
                                         agent_entry_dict[commod],
                                         commod, name, False, True, 1)
