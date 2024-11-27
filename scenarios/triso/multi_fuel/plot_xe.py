import numpy as np
import pandas as pd
import sys
import sqlite3
import os

import matplotlib
matplotlib.use
import matplotlib.pyplot as plt
plt.style.use('plotting.mplstyle')

sys.path.insert(0, '/home/nsryan/Desktop/arfc/transition-scenarios/scripts')
mycolors = ["#332288", "#117733", "#44AA99", "#88CCEE", "#DDCC77", "#CC6677", "#AA4499", "#882255"]

import cymetric as cym
from cymetric import graphs
import transition_metrics as tm
import dataframe_analysis as dta
import nuclides

files = [
    'output/output/dan1_out',
    'output/dal1_out',
    'output/output/da5l1_out',
    'output/output/da15l1_out',
    'output/output/da2d1_out',
    'output/output/da3d1_out'
]

for file in files:
    current_outfile = file + '.sqlite'

    # create a folder for the output files
    output_folder = run_name
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    lwr_list = [
        'Arkansas_Nuclear_One_1', 'Arkansas_Nuclear_One_2', 'Beaver_Valley_1', 'Beaver_Valley_2', 'Big_Rock_Point', 'Braidwood_1', 'Braidwood_2', 'Browns_Ferry_1', 'Browns_Ferry_2', 'Browns_Ferry_3', 'Brunswick_1', 'Brunswick_2', 'Byron_1', 'Byron_2', 'Callaway', 'Calvert_Cliffs_1', 'Calvert_Cliffs_2', 'Catawba_1', 'Catawba_2', 'Clinton_1', 'Columbia', 'Comanche_Peak_1', 'Comanche_Peak_2', 'Cook_1', 'Cook_2', 'Cooper_Station', 'Crystal_River_3', 'Davis_Besse', 'Diablo_Canyon_1', 'Diablo_Canyon_2', 'Dresden_1', 'Dresden_2', 'Dresden_3', 'Duane_Arnold', 'Enrico_Fermi_2', 'Farley_1', 'Farley_2', 'Fitzpatrick', 'Fort_Calhoun', 'Ginna', 'Grand_Gulf_1', 'Haddam_Neck', 'Harris_1', 'Hatch_1', 'Hatch_2', 'Hope_Creek', 'Humboldt_Bay', 'Indian_Point_1', 'Indian_Point_2', 'Indian_Point_3', 'Kewaunee', 'La_Crosse', 'LaSalle_County_1', 'LaSalle_County_2', 'Limerick_1', 'Limerick_2', 'Maine_Yankee', 'McGuire_1', 'McGuire_2', 'Millstone_1', 'Millstone_2', 'Millstone_3', 'Monticello', 'Nine_Mile_Point_1', 'Nine_Mile_Point_2', 'North_Anna_1', 'North_Anna_2', 'Oconee_1', 'Oconee_2', 'Oconee_3', 'Oyster_Creek', 'Palisades', 'Palo_Verde_1', 'Palo_Verde_2', 'Palo_Verde_3', 'Peach_Bottom_2', 'Peach_Bottom_3', 'Perry_1', 'Pilgrim_1', 'Point_Beach_1', 'Point_Beach_2', 'Prairie_Island_1', 'Prairie_Island_2', 'Quad_Cities_1', 'Quad_Cities_2', 'Rancho_Seco', 'River_Bend_1', 'Robinson_2', 'Salem_1', 'Salem_2', 'San_Onofre_1', 'San_Onofre_2', 'San_Onofre_3', 'Seabrook', 'Sequoyah_1', 'Sequoyah_2', 'Shoreham', 'South_Texas_1', 'South_Texas_2', 'St_Lucie_1', 'St_Lucie_2', 'Summer_1', 'Surry_1', 'Surry_2', 'Susquehanna_1', 'Susquehanna_2', 'Three_Mile_Island_1', 'Three_Mile_Island_2', 'Trojan', 'Turkey_Point_3', 'Turkey_Point_4', 'Vermont_Yankee', 'Vogtle_1', 'Vogtle_2', 'Vogtle_3', 'Vogtle_4', 'Waterford_3', 'Watts_Bar_1', 'Watts_Bar_2', 'Wolf_Creek_1', 'Yankee_Rowe', 'Zion_1', 'Zion_2',
    ]

    current_reactors = tm.get_lwr_totals(current_outfile, lwr_list)
    current_reactors = dta.add_year(current_reactors, y0=1958)

    total_lwr = np.zeros(len(current_reactors))
    for reactor in lwr_list:
        for time in range(len(current_reactors)):
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

    cumulative_lwrs = np.cumsum(total_lwr)

    reactor_dict = {
        'time': current_reactors['Year'],
        'total_lwrs': cumulative_lwrs,
        'yearly_lwrs': total_lwr
    }


    # calculate the energy
    current_energy = tm.get_annual_electricity(current_outfile)

    # define energy dict
    energy_dict = {
        'time': current_reactors['Year'],
        'lwr_energy': current_reactors['Energy']
    }

    # now add in xe100 reactors
    current_reactors = tm.get_lwr_totals(current_outfile, ['XE'])
    current_reactors = dta.add_year(current_reactors, y0=1958)

    reactor_dict['yearly_xe'] = current_reactors['Xe100']
