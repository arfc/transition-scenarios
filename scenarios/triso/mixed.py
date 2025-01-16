import numpy as np
import pandas as pd
import sys
import sqlite3

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
import analysis as an
import collections

import nuclides
import fuel_transactions as tran

ad_reactors = {'AP1000':[1117, 0.925, 80, 'no_dist'],'Xe100': [80, 1, 60, 'no_dist'], 'MMR': [5, 1, 20, 'no_dist']}

databases = {
    'one_fuel':{'rand_greed_one': ['drg1', 'drg2', 'drg5', 'drg15', 'drgng']},
    'multi_fuel':{'greedy': ['dg1', 'dg2', 'dg5', 'dg15', 'dgng'],
    'rand_greed': ['drg1', 'drg2', 'drg5', 'drg15', 'drgng'],
    'random': ['dr1', 'dr2', 'dr5', 'dr15', 'drng']},
}


currents = ['Sinks', 'Sink_HLW', 'Sink_LLW', 'Mine', 'Enrichment', 'LWReactors', 'USNC', 'XE', 'AP']

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


for fuel in databases.keys():
    print(fuel)
    for direc in databases[fuel].keys():
        print(direc)
        for file in databases[fuel][direc]:
            print(file)
            
            current_outfile = f'../../../../../../../media/nsryan/Elements/scenes/{direc}/output/{file}_out.sqlite'
            out_base = f'../../../../../../../media/nsryan/Elements/scenes/analysis/{fuel}/{direc}/'


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
            elif 'MMR_enter' in current_reactors.columns:
                for time in range(len(current_reactors)):
                    total_mmrh[time] += current_reactors['MMR_enter'][time]
                    total_mmrh[time] += current_reactors['MMR_exit'][time]
            elif 'MMR' in current_reactors.columns:
                total_mmrh = np.array(current_reactors['MMR'].to_list())
            else:
                pass



            total_ap_reactors = np.zeros(len(current_reactors))
            if 'AP1000_enter' in current_reactors.columns:
                for time in range(len(current_reactors)):
                    total_ap_reactors[time] += current_reactors['AP1000_enter'][time]
                    total_ap_reactors[time] += current_reactors['AP1000_exit'][time]
            elif 'AP1000' in current_reactors.columns:
                total_ap_reactors = np.array(current_reactors['AP1000'].to_list())
            else:
                pass



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
            elif 'Xe100_enter' in current_reactors.columns:
                for time in range(len(current_reactors)):
                    total_xeh[time] += current_reactors['Xe100_enter'][time]
                    total_xeh[time] += current_reactors['Xe100_exit'][time]
            elif 'Xe100' in current_reactors.columns:
                total_xeh = np.array(current_reactors['Xe100'].to_list())
            else:
                pass


            total_reactors = pd.DataFrame({'Year': current_reactors['Year'],
                'LWRs': total_lwr, 'Total LWRs': total_lwr.cumsum(),
                'MMRl': total_mmrl, 'Total MMRl': total_mmrl.cumsum(),
                'MMRh': total_mmrh, 'Total MMRh': total_mmrh.cumsum(),
                'Xe100l': total_xel, 'Total Xe100l': total_xel.cumsum(),
                'Xe100h': total_xeh, 'Total Xe100h': total_xeh.cumsum(),
                'AP1000': total_ap_reactors, 'Total AP1000': total_ap_reactors.cumsum()})

            save = f'reactors/{file}_reactors'
            total_reactors.to_csv(out_base + save + '.csv', index=False)


            plt.plot(current_reactors['Year'], total_lwr.cumsum(), label='LWRs')

            if 'MMRh_enter' in current_reactors.columns:
                plt.plot(current_reactors['Year'], total_mmrh.cumsum(), label='HALEU MMRs')
            if 'MMRl_enter' in current_reactors.columns:
                plt.plot(current_reactors['Year'], total_mmrl.cumsum(), label='LEU+ MMRs LEU')
            if 'MMR' in current_reactors.columns:
                plt.plot(current_reactors['Year'], total_mmr_reactors.cumsum(), label='HALEU MMRs')
            if 'MMR_enter' in current_reactors.columns:
                plt.plot(current_reactors['Year'], total_mmrh.cumsum(), label='HALEU MMRs')

            if 'Xe100h_enter' in current_reactors.columns:
                plt.plot(current_reactors['Year'], total_xeh.cumsum(), label='HALEU Xe100s')
            if 'Xe100l_enter' in current_reactors.columns:
                plt.plot(current_reactors['Year'], total_xel.cumsum(), label='LEU+ Xe100s')
            if 'Xe100_enter' in current_reactors.columns:
                plt.plot(current_reactors['Year'], total_xeh.cumsum(), label='HALEU Xe100s')
            if 'Xe100' in current_reactors.columns:
                plt.plot(current_reactors['Year'], total_xeh.cumsum(), label='HALEU Xe100s')
            if 'Xe100h' in current_reactors.columns:
                plt.plot(current_reactors['Year'], total_xeh.cumsum(), label='HALEU Xe100s')

            if 'AP1000_enter' in current_reactors.columns:
                plt.plot(current_reactors['Year'], total_ap.cumsum(), label='AP1000s')
            if 'AP1000' in current_reactors.columns:
                plt.plot(current_reactors['Year'], total_ap_reactors.cumsum(), label='AP1000s')

            #plt.title('Number of Reactors Deployed')
            plt.xlabel('Year')
            plt.ylabel('Reactors [#]')
            plt.yscale('log')
            plt.legend()

            plt.savefig(out_base + save + '.pdf')
            plt.close()


            current_energy = tm.get_annual_electricity(current_outfile)

            energy_ap = np.zeros(len(total_reactors))

            for time in range(len(total_reactors)):
                if time + ad_reactors['AP1000'][2] * 12 < len(total_reactors):
                    energy_ap[time: time + ad_reactors['AP1000'][2] * 12] += current_reactors['AP1000'][time] * ad_reactors['AP1000'][0]/1000
                else:
                    energy_ap[time:] += current_reactors['AP1000'][time] * ad_reactors['AP1000'][0]/1000

            # convert the monthly energy to annual energy
            energy_ap_ye = energy_ap[::12]
            energy_ap_ye = energy_ap_ye[1:]



            energy_mmrl = np.zeros(len(total_mmrl))
            if 'MMRl_enter' in current_reactors.columns:
                for time in range(len(total_mmrl)):
                    if time + ad_reactors['MMR'][2] * 12 < len(total_mmrl):
                        energy_mmrl[time: time + ad_reactors['MMR'][2] * 12] += current_reactors['MMRl_enter'][time] * ad_reactors['MMR'][0]/1000
                    else:
                        energy_mmrl[time:] += current_reactors['MMRl_enter'][time] * ad_reactors['MMR'][0]

            energy_mmrh = np.zeros(len(total_mmrh))

            if 'MMRh_enter' in current_reactors.columns:
                for time in range(len(total_mmrh)):
                    if time + ad_reactors['MMR'][2] * 12 < len(total_mmrh):
                        energy_mmrh[time: time + ad_reactors['MMR'][2] * 12] += current_reactors['MMRh_enter'][time] * ad_reactors['MMR'][0]/1000
                    else:
                        energy_mmrh[time:] += current_reactors['MMRh_enter'][time] * ad_reactors['MMR'][0]/1000
            if 'MMR_enter' in current_reactors.columns:
                for time in range(len(total_mmrh)):
                    if time + ad_reactors['MMR'][2] * 12 < len(total_mmrh):
                        energy_mmrh[time: time + ad_reactors['MMR'][2] * 12] += current_reactors['MMR_enter'][time] * ad_reactors['MMR'][0]/1000
                    else:
                        energy_mmrh[time:] += current_reactors['MMR_enter'][time] * ad_reactors['MMR'][0]/1000

            energy_mmr_total = energy_mmrl + energy_mmrh

            # convert the monthly energy to annual energy
            energy_mmrh_ye = energy_mmrh[::12]
            energy_mmrh_ye = energy_mmrh_ye[1:]

            energy_mmrl_ye = energy_mmrl[::12]
            energy_mmrl_ye = energy_mmrl_ye[1:]

            energy_mmr_ye_tot = energy_mmr_total[::12]
            energy_mmr_ye_tot = energy_mmr_ye_tot[1:]



            energy_xeh = np.zeros(len(total_xeh))

            if 'Xe100h_enter' in current_reactors.columns:
                for time in range(len(total_xeh)):
                    if time + ad_reactors['Xe100'][2] * 12 < len(total_xeh):
                        energy_xeh[time: time + ad_reactors['Xe100'][2]*12] += current_reactors['Xe100h_enter'][time] * ad_reactors['Xe100'][0]/1000
                    else:
                        energy_xeh[time:] += current_reactors['Xe100h_enter'][time] * ad_reactors['Xe100'][0]/1000
            if 'Xe100_enter' in current_reactors.columns:
                for time in range(len(total_xeh)):
                    if time + ad_reactors['Xe100'][2] * 12 < len(total_xeh):
                        energy_xeh[time: time + ad_reactors['Xe100'][2]*12] += current_reactors['Xe100_enter'][time] * ad_reactors['Xe100'][0]/1000
                    else:
                        energy_xeh[time:] += current_reactors['Xe100_enter'][time] * ad_reactors['Xe100'][0]/1000

            energy_xel = np.zeros(len(total_xel))

            if 'Xe100l_enter' in current_reactors.columns:
                for time in range(len(total_xel)):
                    if time + ad_reactors['Xe100'][2] * 12 < len(total_xel):
                        energy_xel[time: time + ad_reactors['Xe100'][2]*12] += current_reactors['Xe100l_enter'][time] * ad_reactors['Xe100'][0]/1000
                    else:
                        energy_xel[time:] += current_reactors['Xe100l_enter'][time] * ad_reactors['Xe100'][0]/1000


            energy_xe_total = energy_xel + energy_xeh

            # convert the monthly energy to annual energy
            energy_xeh_ye = energy_xeh[::12]
            energy_xeh_ye = energy_xeh_ye[1:]

            energy_xel_ye = energy_xel[::12]
            energy_xel_ye = energy_xel_ye[1:]

            energy_xe_ye_tot = energy_xe_total[::12]
            energy_xe_ye_tot = energy_xe_ye_tot[1:]





            lwr_energy = current_energy['Energy'] - energy_ap_ye - energy_xe_ye_tot - energy_mmr_ye_tot

            total_ar = energy_ap_ye + energy_xe_ye_tot + energy_mmr_ye_tot

            total_energy = pd.DataFrame({'Year': current_energy['Year'],
            'System Energy (GWe-y)': current_energy['Energy'],
            'LWRs (GWe-y)': lwr_energy, 'Total LWRs (GWe-y)': lwr_energy.cumsum(),
            'AP1000 (GWe-y)': energy_ap_ye, 'Total AP1000 (GWe-y)': energy_ap_ye.cumsum(),'Xe100h (GWe-y)': energy_xeh_ye, 'Total Xe100h (GWe-y)': energy_xeh_ye.cumsum(),'Xe100l (GWe-y)': energy_xel_ye, 'Total Xe100l (GWe-y)': energy_xel_ye.cumsum(),'Xe100 (GWe-y)': energy_xe_ye_tot, 'Total Xe100 (GWe-y)': energy_xe_ye_tot.cumsum(),
            'MMRh (GWe-y)': energy_mmrh_ye, 'Total MMRh (GWe-y)': energy_mmrh_ye.cumsum(),
            'MMRl (GWe-y)': energy_mmrl_ye, 'Total MMRl (GWe-y)': energy_mmrl_ye.cumsum(),
            'MMR (GWe-y)': energy_mmr_ye_tot, 'Total MMR (GWe-y)': energy_mmr_ye_tot.cumsum(),
            'ARs (GWe-y)': total_ar, 'Total ARs (GWe-y)': total_ar.cumsum()})

            save = f'energy/{file}_energy'
            total_energy.to_csv(out_base + save + '.csv', index=False)


            total_energy[['Year', 'System Energy (GWe-y)', 'Xe100 (GWe-y)', 'MMR (GWe-y)', 'AP1000 (GWe-y)', 'ARs (GWe-y)']].plot(x='Year', style=['-', '-', '-', '-', '--'])
            plt.yscale('log')
            plt.xlabel('Year')
            plt.ylabel('Energy [GWe-y]')
            plt.legend()

            plt.savefig(out_base + save + '_total_ars' + '.pdf')
            plt.close()



            plt.plot(total_energy['Year'], total_energy['System Energy (GWe-y)'], label='System Energy')

            if 'MMRh_enter' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['MMRh (GWe-y)'], label='HALEU MMRs')
            if 'MMRl_enter' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['MMRl (GWe-y)'], label='LEU+ MMRs')
            if 'MMR' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['MMRh (GWe-y)'], label='HALEU MMRs')
            if 'MMR_enter' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['MMRh (GWe-y)'], label='HALEU MMRs')

            if 'Xe100h_enter' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Xe100h (GWe-y)'], label='HALEU Xe100s')
            if 'Xe100l_enter' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Xe100l (GWe-y)'], label='LEU+ Xe100s')
            if 'Xe100_enter' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Xe100h (GWe-y)'], label='HALEU Xe100s')
            if 'Xe100' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Xe100h (GWe-y)'], label='HALEU Xe100s')
            if 'Xe100h' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Xe100h (GWe-y)'], label='HALEU Xe100s')

            if 'AP1000_enter' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['AP1000 (GWe-y)'], label='AP1000s')
            if 'AP1000' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['AP1000 (GWe-y)'], label='AP1000s')


            plt.yscale('log')
            #plt.title('Energy Generation Each Year')
            plt.xlabel('Year')
            plt.ylabel('Energy [GWe-y]')
            plt.legend()

            plt.savefig(out_base + save + '_by_fuel' + '.pdf')
            plt.close()



            plt.plot(total_energy['Year'], total_energy['System Energy (GWe-y)'].cumsum(), label='System Energy')


            if 'MMRh_enter' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Total MMRh (GWe-y)'], label='HALEU MMRs')
            if 'MMRl_enter' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Total MMRl (GWe-y)'], label='LEU+ MMRs')
            if 'MMR' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Total MMRh (GWe-y)'], label='HALEU MMRs')
            if 'MMR_enter' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Total MMRh (GWe-y)'], label='HALEU MMRs')

            if 'Xe100h_enter' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Total Xe100h (GWe-y)'], label='HALEU Xe100s')
            if 'Xe100l_enter' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Total Xe100l (GWe-y)'], label='LEU+ Xe100s')
            if 'Xe100_enter' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Total Xe100h (GWe-y)'], label='HALEU Xe100s')
            if 'Xe100' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Total Xe100h (GWe-y)'], label='HALEU Xe100s')
            if 'Xe100h' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Total Xe100h (GWe-y)'], label='HALEU Xe100s')

            if 'AP1000_enter' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Total AP1000 (GWe-y)'], label='AP1000s')
            if 'AP1000' in current_reactors.columns:
                plt.plot(total_energy['Year'], total_energy['Total AP1000 (GWe-y)'], label='AP1000s')

            plt.plot(total_energy['Year'], total_energy['Total ARs (GWe-y)'], label='ARs', linestyle='--')


            plt.yscale('log')
            #plt.title('Energy Generation Each Year')
            plt.xlabel('Year')
            plt.ylabel('Cumulative Energy [GWe-y]')
            plt.legend()

            plt.savefig(out_base + save + '_cumulative_by_fuel' + '.pdf')
            plt.close()



            current_transactions = tm.add_receiver_prototype(current_outfile)


            current_uox = dta.commodity_mass_traded(current_transactions, 'fresh_uox')


            current_ap_uox = dta.commodity_mass_traded(current_transactions, 'fresh_ap_uox')


            current_xe_leup = dta.commodity_mass_traded(current_transactions, 'fresh_xe100_leup')
            current_xe_haleu = dta.commodity_mass_traded(current_transactions, 'fresh_xe100_haleu')


            current_mmr_leup = dta.commodity_mass_traded(current_transactions, 'fresh_mmr_leup')
            current_mmr_haleu = dta.commodity_mass_traded(current_transactions, 'fresh_mmr_haleu')


            total_fresh = pd.DataFrame({'Year': current_uox['Year'],
            'UOx': current_uox['Quantity'], 'Total UOx': current_uox['Quantity'].cumsum(),
            'AP UOx': current_ap_uox['Quantity'], 'Total AP UOx': current_ap_uox['Quantity'].cumsum(),
            'Xe100h': current_xe_haleu['Quantity'], 'Total Xe100h': current_xe_haleu['Quantity'].cumsum(),
            'Xe100l': current_xe_leup['Quantity'], 'Total Xe100l': current_xe_leup['Quantity'].cumsum(),
            'MMRh': current_mmr_haleu['Quantity'], 'Total MMRh': current_mmr_haleu['Quantity'].cumsum(),
            'MMRl': current_mmr_leup['Quantity'], 'Total MMRl': current_mmr_leup['Quantity'].cumsum()})

            save = f'fresh/{file}_fresh_fuel'
            total_fresh.to_csv(out_base + save + '.csv', index=False)




            plt.plot(total_fresh['Year'], total_fresh['UOx'].cumsum()/1000, label='LWR LEU')

            if 'MMRh_enter' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Total MMRh']/1000, label='HALEU MMRs')
            if 'MMRl_enter' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Total MMRl']/1000, label='LEU+ MMRs')
            if 'MMR' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Total MMRh']/1000, label='HALEU MMRs')
            if 'MMR_enter' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Total MMRh']/1000, label='HALEU MMRs')

            if 'Xe100h_enter' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Total Xe100h']/1000, label='HALEU Xe100s')
            if 'Xe100l_enter' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Total Xe100l']/1000, label='LEU+ Xe100s')
            if 'Xe100_enter' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Total Xe100h']/1000, label='HALEU Xe100s')
            if 'Xe100' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Total Xe100h']/1000, label='HALEU Xe100s')
            if 'Xe100h' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Total Xe100h']/1000, label='HALEU Xe100s')

            if 'AP1000_enter' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Total AP UOx']/1000, label='AP1000s')
            if 'AP1000' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Total AP UOx']/1000, label='AP1000 LEU')

            plt.legend() #(loc=2)
            plt.ylabel('Mass Fresh Fuel [t]')
            plt.xlabel('Year')
            plt.yscale('log')

            plt.savefig(out_base + save + '_cumulative_by_fuel' + '.pdf')
            plt.close()




            plt.plot(total_fresh['Year'], total_fresh['UOx']/1000, label='LWR LEU')

            if 'MMRh_enter' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['MMRh']/1000, label='HALEU MMRs')
            if 'MMRl_enter' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['MMRl']/1000, label='LEU+ MMRs')
            if 'MMR' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['MMRh']/1000, label='HALEU MMRs')
            if 'MMR_enter' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['MMRh']/1000, label='HALEU MMRs')

            if 'Xe100h_enter' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Xe100h']/1000, label='HALEU Xe100s')
            if 'Xe100l_enter' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Xe100l']/1000, label='LEU+ Xe100s')
            if 'Xe100_enter' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Xe100h']/1000, label='HALEU Xe100s')
            if 'Xe100' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Xe100h']/1000, label='HALEU Xe100s')
            if 'Xe100h' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['Xe100h']/1000, label='HALEU Xe100s')

            if 'AP1000_enter' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['AP UOx']/1000, label='AP1000 LEU')
            if 'AP1000' in current_reactors.columns:
                plt.plot(total_fresh['Year'], total_fresh['AP UOx']/1000, label='AP1000 LEU')

            plt.legend() #(loc=2)
            plt.ylabel('Mass Fresh Fuel [t]')
            plt.xlabel('Year')
            plt.yscale('log')

            plt.savefig(out_base + save + '_by_fuel' + '.pdf')
            plt.close()



            used_uox = dta.commodity_mass_traded(current_transactions, 'used_uox')


            used_ap_uox = dta.commodity_mass_traded(current_transactions, 'used_ap_uox')


            used_xe_leup = dta.commodity_mass_traded(current_transactions, 'used_xe100_leup')
            used_xe_haleu = dta.commodity_mass_traded(current_transactions, 'used_xe100_haleu')



            used_mmr_leup = dta.commodity_mass_traded(current_transactions, 'used_mmr_leup')
            used_mmr_haleu = dta.commodity_mass_traded(current_transactions, 'used_mmr_haleu')


            total_used = pd.DataFrame({'Year': current_reactors['Year'],
            'UOx': used_uox['Quantity'], 'Total UOx': used_uox['Quantity'].cumsum(),
            'Xe100h': used_xe_haleu['Quantity'], 'Total Xe100h': used_xe_haleu['Quantity'].cumsum(),
            'Xe100l': used_xe_leup['Quantity'], 'Total Xe100l': used_xe_leup['Quantity'].cumsum(),
            'MMRh': used_mmr_haleu['Quantity'], 'Total MMRh': used_mmr_haleu['Quantity'].cumsum(),
            'MMRl': used_mmr_leup['Quantity'], 'Total MMRl': used_mmr_leup['Quantity'].cumsum(),
            'AP UOx': used_ap_uox['Quantity'], 'Total AP UOx': used_ap_uox['Quantity'].cumsum()})

            save = f'used/{file}_used_fuel'
            total_used.to_csv(out_base + save + '.csv', index=False)




            plt.plot(total_used['Year'], total_used['UOx'].cumsum()/1000, label='LWR LEU')

            if 'MMRh_enter' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Total MMRh']/1000, label='HALEU MMRs')
            if 'MMRl_enter' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Total MMRl']/1000, label='LEU+ MMRs')
            if 'MMR' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Total MMRh']/1000, label='HALEU MMRs')
            if 'MMR_enter' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Total MMRh']/1000, label='HALEU MMRs')

            if 'Xe100h_enter' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Total Xe100h']/1000, label='HALEU Xe100s')
            if 'Xe100l_enter' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Total Xe100l']/1000, label='LEU+ Xe100s')
            if 'Xe100_enter' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Total Xe100h']/1000, label='HALEU Xe100s')
            if 'Xe100' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Total Xe100h']/1000, label='HALEU Xe100s')
            if 'Xe100h' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Total Xe100h']/1000, label='HALEU Xe100s')

            if 'AP1000_enter' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Total AP UOx']/1000, label='AP1000 LEU')
            if 'AP1000' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Total AP UOx']/1000, label='AP1000 LEU')

            plt.legend() #(loc=2)
            plt.ylabel('Mass Fresh Fuel [t]')
            plt.xlabel('Year')
            plt.yscale('log')

            plt.savefig(out_base + save + '_cumulative_by_fuel' + '.pdf')
            plt.close()



            plt.plot(total_used['Year'], total_used['UOx']/1000, label='LWR LEU')

            if 'MMRh_enter' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['MMRh']/1000, label='HALEU MMRs')
            if 'MMRl_enter' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['MMRl']/1000, label='LEU+ MMRs')
            if 'MMR' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['MMRh']/1000, label='HALEU MMRs')
            if 'MMR_enter' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['MMRh']/1000, label='HALEU MMRs')

            if 'Xe100h_enter' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Xe100h']/1000, label='HALEU Xe100s')
            if 'Xe100l_enter' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Xe100l']/1000, label='LEU+ Xe100s')
            if 'Xe100_enter' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Xe100h']/1000, label='HALEU Xe100s')
            if 'Xe100' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Xe100h']/1000, label='HALEU Xe100s')
            if 'Xe100h' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['Xe100h']/1000, label='HALEU Xe100s')

            if 'AP1000_enter' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['AP UOx']/1000, label='AP1000s')
            if 'AP1000' in current_reactors.columns:
                plt.plot(total_used['Year'], total_used['AP UOx']/1000, label='AP1000 LEU')

            plt.legend() #(loc=2)
            plt.ylabel('Mass Fresh Fuel [t]')
            plt.xlabel('Year')
            plt.yscale('log')

            plt.savefig(out_base + save + '_by_fuel' + '.pdf')
            plt.close()



            #Defining assays for LEU product, tails, and feed material
            leu_p = 0.045
            mmrh_p = 0.1975
            mmrl_p = 0.0995
            xeh_p = 0.155
            xel_p = 0.0995
            x_f = 0.00711
            x_t = 0.002



            current_tails_lwr = dta.calculate_tails(current_uox['Quantity'], leu_p, x_t, x_f)
            current_feed_lwr = dta.calculate_feed(current_uox['Quantity'], current_tails_lwr)
            current_swu_lwr = dta.calculate_SWU(current_uox['Quantity'], leu_p,
                                        current_tails_lwr, x_t,
                                        current_feed_lwr, x_f)
            current_swu_lwr = current_swu_lwr.to_frame().reset_index()
            current_swu_lwr = current_swu_lwr.rename(columns={'Quantity':'SWU', 'index':'Time'})
            current_swu_lwr = dta.add_year(current_swu_lwr)



            current_tails_ap = dta.calculate_tails(current_ap_uox['Quantity'], leu_p, x_t, x_f)
            current_feed_ap = dta.calculate_feed(current_ap_uox['Quantity'], current_tails_ap)
            current_swu_ap = dta.calculate_SWU(current_ap_uox['Quantity'], leu_p,
                                        current_tails_ap, x_t,
                                        current_feed_ap, x_f)
            current_swu_ap = current_swu_ap.to_frame().reset_index()
            current_swu_ap = current_swu_ap.rename(columns={'Quantity':'SWU', 'index':'Time'})
            current_swu_ap = dta.add_year(current_swu_ap)



            current_tails_mmrh = dta.calculate_tails(current_mmr_haleu['Quantity'], mmrh_p, x_t, x_f)
            current_feed_mmrh = dta.calculate_feed(current_mmr_haleu['Quantity'], current_tails_mmrh)
            current_swu_mmrh = dta.calculate_SWU(current_mmr_haleu['Quantity'], mmrh_p,
                                        current_tails_mmrh, x_t,
                                        current_feed_mmrh, x_f)
            current_swu_mmrh = current_swu_mmrh.to_frame().reset_index()
            current_swu_mmrh = current_swu_mmrh.rename(columns={'Quantity':'SWU', 'index':'Time'})
            current_swu_mmrh = dta.add_year(current_swu_mmrh)



            current_tails_mmrl = dta.calculate_tails(current_mmr_leup['Quantity'], mmrl_p, x_t, x_f)
            current_feed_mmrl = dta.calculate_feed(current_mmr_leup['Quantity'], current_tails_mmrl)
            current_swu_mmrl = dta.calculate_SWU(current_mmr_leup['Quantity'], mmrl_p,
                                        current_tails_mmrl, x_t,
                                        current_feed_mmrl, x_f)
            current_swu_mmrl = current_swu_mmrl.to_frame().reset_index()
            current_swu_mmrl = current_swu_mmrl.rename(columns={'Quantity':'SWU', 'index':'Time'})
            current_swu_mmrl = dta.add_year(current_swu_mmrl)



            current_tails_xeh = dta.calculate_tails(current_xe_haleu['Quantity'], xeh_p, x_t, x_f)
            current_feed_xeh = dta.calculate_feed(current_xe_haleu['Quantity'], current_tails_xeh)
            current_swu_xeh = dta.calculate_SWU(current_xe_haleu['Quantity'], xeh_p,
                                        current_tails_xeh, x_t,
                                        current_feed_xeh, x_f)
            current_swu_xeh = current_swu_xeh.to_frame().reset_index()
            current_swu_xeh = current_swu_xeh.rename(columns={'Quantity':'SWU', 'index':'Time'})
            current_swu_xeh = dta.add_year(current_swu_xeh)



            current_tails_xel = dta.calculate_tails(current_xe_leup['Quantity'], xel_p, x_t, x_f)
            current_feed_xel = dta.calculate_feed(current_xe_leup['Quantity'], current_tails_xel)
            current_swu_xel = dta.calculate_SWU(current_xe_leup['Quantity'], xel_p,
                                        current_tails_xel, x_t,
                                        current_feed_xel, x_f)
            current_swu_xel = current_swu_xel.to_frame().reset_index()
            current_swu_xel = current_swu_xel.rename(columns={'Quantity':'SWU', 'index':'Time'})
            current_swu_xel = dta.add_year(current_swu_xel)



            total_swu = pd.DataFrame({'Year': current_reactors['Year'],
            'UOx SWU': current_swu_lwr['SWU'], 'Total UOx SWU': current_swu_lwr['SWU'].cumsum(),
            'Xe100h SWU': current_swu_xeh['SWU'], 'Total Xe100h SWU': current_swu_xeh['SWU'].cumsum(),
            'Xe100l SWU': current_swu_xel['SWU'], 'Total Xe100l SWU': current_swu_xel['SWU'].cumsum(),
            'AP UOx SWU': current_swu_ap['SWU'], 'Total AP UOx SWU': current_swu_ap['SWU'].cumsum(),
            'MMRh SWU': current_swu_mmrh['SWU'], 'Total MMRh SWU': current_swu_mmrh['SWU'].cumsum(),
            'MMRl SWU': current_swu_mmrl['SWU'], 'Total MMRl SWU': current_swu_mmrl['SWU'].cumsum()})

            save = f'swu/{file}_swu'
            total_swu.to_csv(out_base + save + '.csv', index=False)



            plt.plot(total_swu['Year'], total_swu['UOx SWU'].cumsum(), label='LWR LEU')

            if 'MMRh_enter' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Total MMRh SWU'], label='HALEU MMRs')
            if 'MMRl_enter' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Total MMRl SWU'], label='LEU+ MMRs')
            if 'MMR' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Total MMRh SWU'], label='HALEU MMRs')
            if 'MMR_enter' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Total MMRh SWU'], label='HALEU MMRs')

            if 'Xe100h_enter' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Total Xe100h SWU'], label='HALEU Xe100s')
            if 'Xe100l_enter' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Total Xe100l SWU'], label='LEU+ Xe100s')
            if 'Xe100_enter' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Total Xe100h SWU'], label='HALEU Xe100s')
            if 'Xe100' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Total Xe100h SWU'], label='HALEU Xe100s')
            if 'Xe100h' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Total Xe100h SWU'], label='HALEU Xe100s')

            if 'AP1000_enter' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Total AP UOx SWU'], label='AP1000 LEU')
            if 'AP1000' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Total AP UOx SWU'], label='AP1000 LEU')

            plt.legend() #(loc=2)
            plt.ylabel('SWU [kg-SWU]')
            plt.xlabel('Year')
            plt.yscale('log')

            plt.savefig(out_base + save + '_cumulative_by_fuel' + '.pdf')
            plt.close()



            plt.plot(total_swu['Year'], total_swu['UOx SWU'], label='LWR LEU')

            if 'MMRh_enter' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['MMRh SWU'], label='HALEU MMRs')
            if 'MMRl_enter' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['MMRl SWU'], label='LEU+ MMRs')
            if 'MMR' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['MMRh SWU'], label='HALEU MMRs')
            if 'MMR_enter' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['MMRh SWU'], label='HALEU MMRs')

            if 'Xe100h_enter' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Xe100h SWU'], label='HALEU Xe100s')
            if 'Xe100l_enter' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Xe100l SWU'], label='LEU+ Xe100s')
            if 'Xe100_enter' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Xe100h SWU'], label='HALEU Xe100s')
            if 'Xe100' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Xe100h SWU'], label='HALEU Xe100s')
            if 'Xe100h' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['Xe100h SWU'], label='HALEU Xe100s')

            if 'AP1000_enter' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['AP UOx SWU'], label='AP1000 LEU')
            if 'AP1000' in current_reactors.columns:
                plt.plot(total_swu['Year'], total_swu['AP UOx SWU'], label='AP1000 LEU')

            plt.legend() #(loc=2)
            plt.ylabel('SWU [kg-SWU]')
            plt.xlabel('Year')
            plt.yscale('log')

            plt.savefig(out_base + save + '_by_fuel' + '.pdf')
            plt.close()