import numpy as np
import pandas as pd
import sys
import sqlite3

import matplotlib
matplotlib.use
import matplotlib.pyplot as plt
plt.style.use('plotting.mplstyle')

sys.path.insert(0, '/home/nsryan/Desktop/arfc/transition-scenarios/scripts')

import cymetric as cym
from cymetric import graphs
import transition_metrics as tm
import dataframe_analysis as dta
import analysis as an
import collections

import fuel_transactions as tran

ad_reactors = {'AP1000':[1117, 0.925, 80, 'no_dist'],'Xe100': [80, 1, 60, 'no_dist'], 'MMR': [5, 1, 20, 'no_dist']}

lwr_list = [
    'Arkansas_Nuclear_One_1','Arkansas_Nuclear_One_2','Beaver_Valley_1','Beaver_Valley_2','Big_Rock_Point','Braidwood_1','Braidwood_2',
    'Browns_Ferry_1','Browns_Ferry_2','Browns_Ferry_3','Brunswick_1',
    'Brunswick_2','Byron_1','Byron_2','Callaway',
    'Calvert_Cliffs_1','Calvert_Cliffs_2','Catawba_1','Catawba_2',
    'Clinton_1','Columbia','Comanche_Peak_1','Comanche_Peak_2',
    'Cook_1','Cook_2','Cooper_Station','Crystal_River_3',
    'Davis_Besse','Diablo_Canyon_1','Diablo_Canyon_2',
    'Dresden_1','Dresden_2','Dresden_3','Duane_Arnold',
    'Enrico_Fermi_2','Farley_1','Farley_2',
    'Fitzpatrick','Fort_Calhoun','Ginna',
    'Grand_Gulf_1','Haddam_Neck','Harris_1',
    'Hatch_1','Hatch_2','Hope_Creek',
    'Humboldt_Bay','Indian_Point_1','Indian_Point_2',
    'Indian_Point_3','Kewaunee','La_Crosse',
    'LaSalle_County_1','LaSalle_County_2','Limerick_1',
    'Limerick_2','Maine_Yankee','McGuire_1',
    'McGuire_2','Millstone_1','Millstone_2',
    'Millstone_3','Monticello','Nine_Mile_Point_1',
    'Nine_Mile_Point_2','North_Anna_1','North_Anna_2',
    'Oconee_1','Oconee_2','Oconee_3',
    'Oyster_Creek','Palisades','Palo_Verde_1','Palo_Verde_2',
    'Palo_Verde_3','Peach_Bottom_2','Peach_Bottom_3','Perry_1',
    'Pilgrim_1','Point_Beach_1','Point_Beach_2','Prairie_Island_1',
    'Prairie_Island_2','Quad_Cities_1','Quad_Cities_2','Rancho_Seco',
    'River_Bend_1','Robinson_2','Salem_1','Salem_2','San_Onofre_1',
    'San_Onofre_2','San_Onofre_3','Seabrook','Sequoyah_1',
    'Sequoyah_2','Shoreham','South_Texas_1','South_Texas_2',
    'St_Lucie_1','St_Lucie_2','Summer_1','Surry_1','Surry_2',
    'Susquehanna_1','Susquehanna_2','Three_Mile_Island_1','Three_Mile_Island_2',
    'Trojan','Turkey_Point_3','Turkey_Point_4','Vermont_Yankee','Vogtle_1',
    'Vogtle_2','Vogtle_3','Vogtle_4','Waterford_3','Watts_Bar_1','Watts_Bar_2',
    'Wolf_Creek_1','Yankee_Rowe','Zion_1','Zion_2'
]

# One fuel single reactor
out_base = '../../../../../../../media/nsryan/Elements/scenes/analysis/one_fuel/single_one/'

## Xe100s
### No growth
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/dan1_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'XE']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_xel = np.zeros(len(current_reactors))
if 'Xe100l_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_xel[time] += current_reactors['Xe100l_enter'][time]
        total_xel[time] += current_reactors['Xe100l_exit'][time]
elif 'Xe100l' in current_reactors.columns:
    total_xel = np.array(current_reactors['Xe100l'].to_list())
else:
    pass

total_xeh = np.zeros(len(current_reactors))
if 'Xe100h_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_xeh[time] += current_reactors['Xe100h_enter'][time]
        total_xeh[time] += current_reactors['Xe100h_exit'][time]
elif 'Xe100h' in current_reactors.columns:
    total_xeh = np.array(current_reactors['Xe100h'].to_list())
else:
    pass

save = 'reactors/dan1_reactors'

total_xe = pd.DataFrame({'Year': current_reactors['Year'],'Xe100h': total_xeh, 'Total_Xe100h': total_xeh.cumsum(), 'Xe100l': total_xel, 'Total_Xe100l': total_xel.cumsum()})

total_xe.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_xeh.cumsum(), label='HALEU Xe100s')
plt.plot(current_reactors['Year'], total_xel.cumsum(), label='LEU+ Xe100s')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')

### 1% growth
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/dal1_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'XE']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_xel = np.zeros(len(current_reactors))
if 'Xe100l_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_xel[time] += current_reactors['Xe100l_enter'][time]
        total_xel[time] += current_reactors['Xe100l_exit'][time]
elif 'Xe100l' in current_reactors.columns:
    total_xel = np.array(current_reactors['Xe100l'].to_list())
else:
    pass

total_xeh = np.zeros(len(current_reactors))
if 'Xe100h_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_xeh[time] += current_reactors['Xe100h_enter'][time]
        total_xeh[time] += current_reactors['Xe100h_exit'][time]
elif 'Xe100h' in current_reactors.columns:
    total_xeh = np.array(current_reactors['Xe100h'].to_list())
else:
    pass

save = 'reactors/dal1_reactors'

total_xe = pd.DataFrame({'Year': current_reactors['Year'],'Xe100h': total_xeh, 'Total_Xe100h': total_xeh.cumsum(), 'Xe100l': total_xel, 'Total_Xe100l': total_xel.cumsum()})

total_xe.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_xeh.cumsum(), label='HALEU Xe100s')
plt.plot(current_reactors['Year'], total_xel.cumsum(), label='LEU+ Xe100s')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')



### 5% growth
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/da5l1_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'XE']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_xel = np.zeros(len(current_reactors))
if 'Xe100l_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_xel[time] += current_reactors['Xe100l_enter'][time]
        total_xel[time] += current_reactors['Xe100l_exit'][time]
elif 'Xe100l' in current_reactors.columns:
    total_xel = np.array(current_reactors['Xe100l'].to_list())
else:
    pass

total_xeh = np.zeros(len(current_reactors))
if 'Xe100h_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_xeh[time] += current_reactors['Xe100h_enter'][time]
        total_xeh[time] += current_reactors['Xe100h_exit'][time]
elif 'Xe100h' in current_reactors.columns:
    total_xeh = np.array(current_reactors['Xe100h'].to_list())
else:
    pass

save = 'reactors/da5l1_reactors'

total_xe = pd.DataFrame({'Year': current_reactors['Year'],'Xe100h': total_xeh, 'Total_Xe100h': total_xeh.cumsum(), 'Xe100l': total_xel, 'Total_Xe100l': total_xel.cumsum()})

total_xe.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_xeh.cumsum(), label='HALEU Xe100s')
plt.plot(current_reactors['Year'], total_xel.cumsum(), label='LEU+ Xe100s')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')



### 15% growth
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/da15l1_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'XE']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_xel = np.zeros(len(current_reactors))
if 'Xe100l_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_xel[time] += current_reactors['Xe100l_enter'][time]
        total_xel[time] += current_reactors['Xe100l_exit'][time]
elif 'Xe100l' in current_reactors.columns:
    total_xel = np.array(current_reactors['Xe100l'].to_list())
else:
    pass

total_xeh = np.zeros(len(current_reactors))
if 'Xe100h_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_xeh[time] += current_reactors['Xe100h_enter'][time]
        total_xeh[time] += current_reactors['Xe100h_exit'][time]
elif 'Xe100h' in current_reactors.columns:
    total_xeh = np.array(current_reactors['Xe100h'].to_list())
else:
    pass

save = 'reactors/da15l1_reactors'

total_xe = pd.DataFrame({'Year': current_reactors['Year'],'Xe100h': total_xeh, 'Total_Xe100h': total_xeh.cumsum(), 'Xe100l': total_xel, 'Total_Xe100l': total_xel.cumsum()})

total_xe.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_xeh.cumsum(), label='HALEU Xe100s')
plt.plot(current_reactors['Year'], total_xel.cumsum(), label='LEU+ Xe100s')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')


### Doubled
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/da2d1_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'XE']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_xel = np.zeros(len(current_reactors))
if 'Xe100l_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_xel[time] += current_reactors['Xe100l_enter'][time]
        total_xel[time] += current_reactors['Xe100l_exit'][time]
elif 'Xe100l' in current_reactors.columns:
    total_xel = np.array(current_reactors['Xe100l'].to_list())
else:
    pass

total_xeh = np.zeros(len(current_reactors))
if 'Xe100h_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_xeh[time] += current_reactors['Xe100h_enter'][time]
        total_xeh[time] += current_reactors['Xe100h_exit'][time]
elif 'Xe100h' in current_reactors.columns:
    total_xeh = np.array(current_reactors['Xe100h'].to_list())
else:
    pass

save = 'reactors/da2d1_reactors'

total_xe = pd.DataFrame({'Year': current_reactors['Year'],'Xe100h': total_xeh, 'Total_Xe100h': total_xeh.cumsum(), 'Xe100l': total_xel, 'Total_Xe100l': total_xel.cumsum()})

total_xe.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_xeh.cumsum(), label='HALEU Xe100s')
plt.plot(current_reactors['Year'], total_xel.cumsum(), label='LEU+ Xe100s')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')


### Tripled
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/da3d1_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'XE']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_xel = np.zeros(len(current_reactors))
if 'Xe100l_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_xel[time] += current_reactors['Xe100l_enter'][time]
        total_xel[time] += current_reactors['Xe100l_exit'][time]
elif 'Xe100l' in current_reactors.columns:
    total_xel = np.array(current_reactors['Xe100l'].to_list())
else:
    pass

total_xeh = np.zeros(len(current_reactors))
if 'Xe100h_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_xeh[time] += current_reactors['Xe100h_enter'][time]
        total_xeh[time] += current_reactors['Xe100h_exit'][time]
elif 'Xe100h' in current_reactors.columns:
    total_xeh = np.array(current_reactors['Xe100h'].to_list())
else:
    pass

save = 'reactors/da3d1_reactors'

total_xe = pd.DataFrame({'Year': current_reactors['Year'],'Xe100h': total_xeh, 'Total_Xe100h': total_xeh.cumsum(), 'Xe100l': total_xel, 'Total_Xe100l': total_xel.cumsum()})

total_xe.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_xeh.cumsum(), label='HALEU Xe100s')
plt.plot(current_reactors['Year'], total_xel.cumsum(), label='LEU+ Xe100s')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')


## MMRs
### No Growth
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/dan2l_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'USNC']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_mmrl = np.zeros(len(current_reactors))
if 'MMRl_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_mmrl[time] += current_reactors['MMRl_enter'][time]
        total_mmrl[time] += current_reactors['MMRl_exit'][time]
elif 'MMRl' in current_reactors.columns:
    total_mmrl = np.array(current_reactors['MMRl'].to_list())
else:
    pass

total_mmrh = np.zeros(len(current_reactors))
if 'MMRh_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_mmrh[time] += current_reactors['MMRh_enter'][time]
        total_mmrh[time] += current_reactors['MMRh_exit'][time]
elif 'MMRh' in current_reactors.columns:
    total_mmrh = np.array(current_reactors['MMRh'].to_list())
else:
    pass

save = 'reactors/dan2_reactors'

total_mmr = pd.DataFrame({'Year': current_reactors['Year'],'MMRh': total_mmrh, 'Total_MMRh': total_mmrh.cumsum(), 'MMRl': total_mmrl, 'Total_MMRl': total_mmrl.cumsum()})

total_mmr.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_mmrh.cumsum(), label='HALEU MMRs')
plt.plot(current_reactors['Year'], total_mmrl.cumsum(), label='LEU+ MMRs')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')


### 1% growth
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/dal2_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'USNC']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_mmrl = np.zeros(len(current_reactors))
if 'MMRl_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_mmrl[time] += current_reactors['MMRl_enter'][time]
        total_mmrl[time] += current_reactors['MMRl_exit'][time]
elif 'MMRl' in current_reactors.columns:
    total_mmrl = np.array(current_reactors['MMRl'].to_list())
else:
    pass

total_mmrh = np.zeros(len(current_reactors))
if 'MMRh_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_mmrh[time] += current_reactors['MMRh_enter'][time]
        total_mmrh[time] += current_reactors['MMRh_exit'][time]
elif 'MMRh' in current_reactors.columns:
    total_mmrh = np.array(current_reactors['MMRh'].to_list())
else:
    pass

save = 'reactors/dal2_reactors'

total_mmr = pd.DataFrame({'Year': current_reactors['Year'],'MMRh': total_mmrh, 'Total_MMRh': total_mmrh.cumsum(), 'MMRl': total_mmrl, 'Total_MMRl': total_mmrl.cumsum()})

total_mmr.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_mmrh.cumsum(), label='HALEU MMRs')
plt.plot(current_reactors['Year'], total_mmrl.cumsum(), label='LEU+ MMRs')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')


### 5% growth
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/da5l2_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'USNC']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_mmrl = np.zeros(len(current_reactors))
if 'MMRl_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_mmrl[time] += current_reactors['MMRl_enter'][time]
        total_mmrl[time] += current_reactors['MMRl_exit'][time]
elif 'MMRl' in current_reactors.columns:
    total_mmrl = np.array(current_reactors['MMRl'].to_list())
else:
    pass

total_mmrh = np.zeros(len(current_reactors))
if 'MMRh_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_mmrh[time] += current_reactors['MMRh_enter'][time]
        total_mmrh[time] += current_reactors['MMRh_exit'][time]
elif 'MMRh' in current_reactors.columns:
    total_mmrh = np.array(current_reactors['MMRh'].to_list())
else:
    pass

save = 'reactors/da5l2_reactors'

total_mmr = pd.DataFrame({'Year': current_reactors['Year'],'MMRh': total_mmrh, 'Total_MMRh': total_mmrh.cumsum(), 'MMRl': total_mmrl, 'Total_MMRl': total_mmrl.cumsum()})

total_mmr.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_mmrh.cumsum(), label='HALEU MMRs')
plt.plot(current_reactors['Year'], total_mmrl.cumsum(), label='LEU+ MMRs')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')


### 15% growth
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/da15l2_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'USNC']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_mmrl = np.zeros(len(current_reactors))
if 'MMRl_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_mmrl[time] += current_reactors['MMRl_enter'][time]
        total_mmrl[time] += current_reactors['MMRl_exit'][time]
elif 'MMRl' in current_reactors.columns:
    total_mmrl = np.array(current_reactors['MMRl'].to_list())
else:
    pass

total_mmrh = np.zeros(len(current_reactors))
if 'MMRh_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_mmrh[time] += current_reactors['MMRh_enter'][time]
        total_mmrh[time] += current_reactors['MMRh_exit'][time]
elif 'MMRh' in current_reactors.columns:
    total_mmrh = np.array(current_reactors['MMRh'].to_list())
else:
    pass

save = 'reactors/da15l2_reactors'

total_mmr = pd.DataFrame({'Year': current_reactors['Year'],'MMRh': total_mmrh, 'Total_MMRh': total_mmrh.cumsum(), 'MMRl': total_mmrl, 'Total_MMRl': total_mmrl.cumsum()})

total_mmr.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_mmrh.cumsum(), label='HALEU MMRs')
plt.plot(current_reactors['Year'], total_mmrl.cumsum(), label='LEU+ MMRs')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')


### Doubled
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/da2d2_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'USNC']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_mmrl = np.zeros(len(current_reactors))
if 'MMRl_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_mmrl[time] += current_reactors['MMRl_enter'][time]
        total_mmrl[time] += current_reactors['MMRl_exit'][time]
elif 'MMRl' in current_reactors.columns:
    total_mmrl = np.array(current_reactors['MMRl'].to_list())
else:
    pass

total_mmrh = np.zeros(len(current_reactors))
if 'MMRh_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_mmrh[time] += current_reactors['MMRh_enter'][time]
        total_mmrh[time] += current_reactors['MMRh_exit'][time]
elif 'MMRh' in current_reactors.columns:
    total_mmrh = np.array(current_reactors['MMRh'].to_list())
else:
    pass

save = 'reactors/da2d2_reactors'

total_mmr = pd.DataFrame({'Year': current_reactors['Year'],'MMRh': total_mmrh, 'Total_MMRh': total_mmrh.cumsum(), 'MMRl': total_mmrl, 'Total_MMRl': total_mmrl.cumsum()})

total_mmr.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_mmrh.cumsum(), label='HALEU MMRs')
plt.plot(current_reactors['Year'], total_mmrl.cumsum(), label='LEU+ MMRs')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')

### Tripled
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/da3d2_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'USNC']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_mmrl = np.zeros(len(current_reactors))
if 'MMRl_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_mmrl[time] += current_reactors['MMRl_enter'][time]
        total_mmrl[time] += current_reactors['MMRl_exit'][time]
elif 'MMRl' in current_reactors.columns:
    total_mmrl = np.array(current_reactors['MMRl'].to_list())

total_mmrh = np.zeros(len(current_reactors))
if 'MMRh_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_mmrh[time] += current_reactors['MMRh_enter'][time]
        total_mmrh[time] += current_reactors['MMRh_exit'][time]
elif 'MMRh' in current_reactors.columns:
    total_mmrh = np.array(current_reactors['MMRh'].to_list())
else:
    pass

save = 'reactors/da3d2_reactors'

total_mmr = pd.DataFrame({'Year': current_reactors['Year'],'MMRh': total_mmrh, 'Total_MMRh': total_mmrh.cumsum(), 'MMRl': total_mmrl, 'Total_MMRl': total_mmrl.cumsum()})

total_mmr.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_mmrh.cumsum(), label='HALEU MMRs')
plt.plot(current_reactors['Year'], total_mmrl.cumsum(), label='LEU+ MMRs')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')


## AP1000s
## No Growth
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/dan3_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'AP']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_ap = np.zeros(len(current_reactors))
if 'AP1000_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_ap[time] += current_reactors['AP1000_enter'][time]
        total_ap[time] += current_reactors['AP1000_exit'][time]
elif 'AP1000' in current_reactors.columns:
    total_ap = np.array(current_reactors['AP1000'].to_list())
else:
    pass

save = 'reactors/dan3_reactors'

total_ap_df = pd.DataFrame({'Year': current_reactors['Year'],'AP1000': total_ap, 'Total_AP1000': total_ap.cumsum()})

total_ap_df.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_ap.cumsum(), label='AP1000s')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
#plt.title('Number of Reactors Deployed')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')


### 1% growth
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/dal3_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'AP']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_ap = np.zeros(len(current_reactors))
if 'AP1000_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_ap[time] += current_reactors['AP1000_enter'][time]
        total_ap[time] += current_reactors['AP1000_exit'][time]
elif 'AP1000' in current_reactors.columns:
    total_ap = np.array(current_reactors['AP1000'].to_list())
else:
    pass

save = 'reactors/dal3_reactors'

total_ap_df = pd.DataFrame({'Year': current_reactors['Year'],'AP1000': total_ap, 'Total_AP1000': total_ap.cumsum()})

total_ap_df.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_ap.cumsum(), label='AP1000s')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
#plt.title('Number of Reactors Deployed')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')

### 5% growth
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/da5l3_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'AP']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_ap = np.zeros(len(current_reactors))
if 'AP1000_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_ap[time] += current_reactors['AP1000_enter'][time]
        total_ap[time] += current_reactors['AP1000_exit'][time]
elif 'AP1000' in current_reactors.columns:
    total_ap = np.array(current_reactors['AP1000'].to_list())
else:
    pass

save = 'reactors/da5l3_reactors'

total_ap_df = pd.DataFrame({'Year': current_reactors['Year'],'AP1000': total_ap, 'Total_AP1000': total_ap.cumsum()})

total_ap_df.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_ap.cumsum(), label='AP1000s')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
#plt.title('Number of Reactors Deployed')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')


### 15% growth
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/da15l3_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'AP']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_ap = np.zeros(len(current_reactors))
if 'AP1000_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_ap[time] += current_reactors['AP1000_enter'][time]
        total_ap[time] += current_reactors['AP1000_exit'][time]
elif 'AP1000' in current_reactors.columns:
    total_ap = np.array(current_reactors['AP1000'].to_list())
else:
    pass

save = 'reactors/da15l3_reactors'

total_ap_df = pd.DataFrame({'Year': current_reactors['Year'],'AP1000': total_ap, 'Total_AP1000': total_ap.cumsum()})

total_ap_df.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_ap.cumsum(), label='AP1000s')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
#plt.title('Number of Reactors Deployed')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')


### Doubled
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/da2d3_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'AP']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_ap = np.zeros(len(current_reactors))
if 'AP1000_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_ap[time] += current_reactors['AP1000_enter'][time]
        total_ap[time] += current_reactors['AP1000_exit'][time]
elif 'AP1000' in current_reactors.columns:
    total_ap = np.array(current_reactors['AP1000'].to_list())
else:
    pass

save = 'reactors/da2d3_reactors'

total_ap_df = pd.DataFrame({'Year': current_reactors['Year'],'AP1000': total_ap, 'Total_AP1000': total_ap.cumsum()})

total_ap_df.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_ap.cumsum(), label='AP1000s')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
#plt.title('Number of Reactors Deployed')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')


### Tripled
current_outfile = '../../../../../../../media/nsryan/Elements/scenes/single_reactor/one_fuel/output/da3d3_out.sqlite'

currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'AP']

current_reactors = tm.get_lwr_totals(current_outfile, currents)
current_reactors = dta.add_year(current_reactors, y0=1958)

total_lwr = np.zeros(len(current_reactors))
for reactor in lwr_list:
    for time in range(len(current_reactors)):
        if reactor == 'Vogtle_4':
            total_lwr[time] += current_reactors[reactor][time]
        else:
            total_lwr[time] += current_reactors[reactor + '_enter'][time]
            total_lwr[time] += current_reactors[reactor + '_exit'][time]

total_ap = np.zeros(len(current_reactors))
if 'AP1000_enter' in current_reactors.columns:
    for time in range(len(current_reactors)):
        total_ap[time] += current_reactors['AP1000_enter'][time]
        total_ap[time] += current_reactors['AP1000_exit'][time]
elif 'AP1000' in current_reactors.columns:
    total_ap = np.array(current_reactors['AP1000'].to_list())
else:
    pass

save = 'reactors/da3d3_reactors'

total_ap_df = pd.DataFrame({'Year': current_reactors['Year'],'AP1000': total_ap, 'Total_AP1000': total_ap.cumsum()})

total_ap_df.to_csv(out_base + save + '.csv', index=False)

plt.plot(current_reactors['Year'], total_ap.cumsum(), label='AP1000s')

plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')
#plt.title('Number of Reactors Deployed')
plt.xlabel('Year')
plt.ylabel('Reactors [#]')
plt.yscale('log')
plt.legend()

plt.savefig(out_base + save + '.pdf')
