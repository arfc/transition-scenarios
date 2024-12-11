import numpy as np
import pandas as pd
import sys
import matplotlib
matplotlib.use
import matplotlib.pyplot as plt
plt.style.use('../plotting.mplstyle')

sys.path.insert(0,'../../../scripts')

import reactor_deployment as dep
import scenario_definitions as sd

# read in the LWR deployment data so we can establish a baseline.
lwr_df = pd.read_csv('lwr_info.csv')

# Remove the 'Unnamed: 0' column
lwr_df = lwr_df.drop('Unnamed: 0', axis=1)

lwr_df['retirement_year'] = lwr_df['Actual retirement (year)'].fillna(
    lwr_df['Startup date (year) b'] + 80)

capacity_change = {year: 0 for year in range(sd.sim_start_yr, sd.sim_end_yr)}

# calculate the decommissioned capacity for each retirement year
for year, power in zip(lwr_df['retirement_year'], lwr_df['power_cap(MWe)']):
    capacity_change[int(year)] -= power * sd.lwr_capacity_factor

# calculate the commissioned LWR capacity for each startup year
for year, power in zip(lwr_df['Startup date (year) b'], lwr_df['power_cap(MWe)']):
    capacity_change[int(year)] += power * sd.lwr_capacity_factor

# Convert to a pandas DataFrame and plot.
capacity_change_df = pd.DataFrame(capacity_change.values(), index=capacity_change.keys(), columns=['new_LWR_Capacity'])

# create a total lwr capacity column
capacity_change_df['Total LWR Capacity'] = capacity_change_df['new_LWR_Capacity'].cumsum()

# create a time step column that subtracts the start year from the current year and multiplies by 12
capacity_change_df['time_step'] = (capacity_change_df.index - sd.sim_start_yr) * 12

# create a function that will generate the deployinst.xml file for each reactor column by reading in the number of reactors at each time step and converting it into a deployinst.xml file
def generate_deployinst_xml(df, reactor_name, transition_year=sd.transition_year, end_year=sd.sim_end_yr):
  start_row = int(transition_year) + 1
  deployinst_xml = """<DeployInst>
               <prototypes>"""

  for year in range(transition_year, end_year):
    if df.loc[year, f'{reactor}_new'] != 0:
      deployinst_xml += f"""
                  <val>{reactor_name}</val>"""

  deployinst_xml += """
               </prototypes>
               <build_times>"""

  for year in range(transition_year, end_year):
    if df.loc[year, f'{reactor}_new'] != 0:
      deployinst_xml += f"""
                <val>{df.loc[year,'time_step']}</val>"""

  deployinst_xml += """
               </build_times>
               <n_build>"""

  for year in range(transition_year, end_year):
    if df.loc[year, f'{reactor}_new'] != 0:
      deployinst_xml += f"""
                <val>{int(df.loc[year, f'{reactor}_new'])}</val>"""

  deployinst_xml += """
               </n_build>
             </DeployInst>"""

  return deployinst_xml.strip()



# # No Growth

base_capacity = capacity_change_df.loc[sd.transition_year, 'Total LWR Capacity'] # in MWe

print(f"Total LWR capacity in {sd.transition_year}: {base_capacity} MWe")

no_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=no_growth_cap_df, base_col='Total LWR Capacity', rate=1, start_year=sd.transition_year, end_year=sd.sim_end_yr)

for reactor in sd.ad_reactors.keys():
    no_growth_cap_df[f'{reactor}'] = np.ceil(no_growth_cap_df['New Capacity Inc 1']/sd.ad_reactors[reactor][0])

for reactor in sd.ad_reactors.keys():
    no_growth_cap_df[f'{reactor}_new'] = no_growth_cap_df[f'{reactor}'].diff()

no_growth_cap_df['AP1000_new_cap'] = no_growth_cap_df['AP1000_new'] * sd.ad_reactors['AP1000'][0]
no_growth_cap_df['Xe100_new_cap'] = no_growth_cap_df['Xe100_new'] * sd.ad_reactors['Xe100'][0]
no_growth_cap_df['MMR_new_cap'] = no_growth_cap_df['MMR_new'] * sd.ad_reactors['MMR'][0]

no_growth_cap_df['AP1000_new_cap_total'] = no_growth_cap_df['AP1000_new_cap'].cumsum()
no_growth_cap_df['Xe100_new_cap_total'] = no_growth_cap_df['Xe100_new_cap'].cumsum()
no_growth_cap_df['MMR_new_cap_total'] = no_growth_cap_df['MMR_new_cap'].cumsum()

no_growth_cap_df[['time_step','Total LWR Capacity Inc 1','AP1000_new_cap_total', 'Xe100_new_cap_total', 'MMR_new_cap_total']].plot(x='time_step')

output_dir = '../single_reactor/one_fuel/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(no_growth_cap_df, reactor)
    with open(f'{output_dir}ng_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Greedy

greedy_no_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_no_growth_cap_df, base_col='Total LWR Capacity', rate=1, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_no_growth_cap_df = greedy_no_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.greedy_deployment(df=greedy_no_growth_cap_df, base_col='New Capacity Inc 1', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year)

for reactor in sd.ad_reactors.keys():
    greedy_no_growth_cap_df[f'{reactor}_new'] = greedy_no_growth_cap_df[f'num_{reactor}']

greedy_no_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../greedy/ng/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_low_growth_cap_df, reactor)
    with open(f'{output_dir}ng_greedy_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Rand + Greedy

greedy_no_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_no_growth_cap_df, base_col='Total LWR Capacity', rate=1, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_no_growth_cap_df = greedy_no_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.rand_greedy_deployment(df=greedy_no_growth_cap_df, base_col='New Capacity Inc 1', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year, set_seed=True)

for reactor in sd.ad_reactors.keys():
    greedy_no_growth_cap_df[f'{reactor}_new'] = greedy_no_growth_cap_df[f'num_{reactor}']

greedy_no_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../rand_greed/ng/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_low_growth_cap_df, reactor)
    with open(f'{output_dir}ng_rand_greedy_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Random

greedy_no_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_no_growth_cap_df, base_col='Total LWR Capacity', rate=1, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_no_growth_cap_df = greedy_no_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.rand_deployment(df=greedy_no_growth_cap_df, base_col='New Capacity Inc 1', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year, set_seed=True)

for reactor in sd.ad_reactors.keys():
    greedy_no_growth_cap_df[f'{reactor}_new'] = greedy_no_growth_cap_df[f'num_{reactor}']

greedy_no_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../random/ng/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_low_growth_cap_df, reactor)
    with open(f'{output_dir}ng_random_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# # 1 % Growth

low_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=low_growth_cap_df, base_col='Total LWR Capacity', rate=1.01, start_year=sd.transition_year, end_year=sd.sim_end_yr)

for reactor in sd.ad_reactors.keys():
    low_growth_cap_df[f'{reactor}'] = np.ceil(low_growth_cap_df['New Capacity Inc 1.01']/sd.ad_reactors[reactor][0])

for reactor in sd.ad_reactors.keys():
    low_growth_cap_df[f'{reactor}_new'] = low_growth_cap_df[f'{reactor}'].diff()

output_dir = '../single_reactor/one_fuel/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(low_growth_cap_df, reactor)
    with open(f'{output_dir}lg_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Greedy

greedy_low_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_low_growth_cap_df, base_col='Total LWR Capacity', rate=1.01, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_low_growth_cap_df = greedy_low_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.greedy_deployment(df=greedy_low_growth_cap_df, base_col='New Capacity Inc 1.01', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year)

for reactor in sd.ad_reactors.keys():
    greedy_low_growth_cap_df[f'{reactor}_new'] = greedy_low_growth_cap_df[f'num_{reactor}']

greedy_low_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../greedy/one/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_low_growth_cap_df, reactor)
    with open(f'{output_dir}lg_greedy_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Rand + Greedy

greedy_low_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_low_growth_cap_df, base_col='Total LWR Capacity', rate=1.01, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_low_growth_cap_df = greedy_low_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.rand_greedy_deployment(df=greedy_low_growth_cap_df, base_col='New Capacity Inc 1.01', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year, set_seed=True)

for reactor in sd.ad_reactors.keys():
    greedy_low_growth_cap_df[f'{reactor}_new'] = greedy_low_growth_cap_df[f'num_{reactor}']

greedy_low_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../rand_greed/one/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_low_growth_cap_df, reactor)
    with open(f'{output_dir}lg_rand_greedy_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Random

greedy_low_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_low_growth_cap_df, base_col='Total LWR Capacity', rate=1.01, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_low_growth_cap_df = greedy_low_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.rand_deployment(df=greedy_low_growth_cap_df, base_col='New Capacity Inc 1.01', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year, set_seed=True)

for reactor in sd.ad_reactors.keys():
    greedy_low_growth_cap_df[f'{reactor}_new'] = greedy_low_growth_cap_df[f'num_{reactor}']

greedy_low_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../random/one/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_low_growth_cap_df, reactor)
    with open(f'{output_dir}lg_random_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# # 5% Growth by 2050

rate = 1.05**(1/(2050-2022))
print(f"Rate of growth: {rate}")

med_5_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=med_5_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

for reactor in sd.ad_reactors.keys():
    med_5_growth_cap_df[f'{reactor}'] = np.ceil(med_5_growth_cap_df[f'New Capacity Inc {rate}']/sd.ad_reactors[reactor][0])

for reactor in sd.ad_reactors.keys():
    med_5_growth_cap_df[f'{reactor}_new'] = med_5_growth_cap_df[f'{reactor}'].diff()

output_dir = '../single_reactor/one_fuel/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(med_5_growth_cap_df, reactor)
    with open(f'{output_dir}m5g_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Greedy

greedy_mg5_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_mg5_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_mg5_growth_cap_df = greedy_mg5_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.greedy_deployment(df=greedy_mg5_growth_cap_df, base_col='New Capacity Inc 1.0017440249087228', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year)

for reactor in sd.ad_reactors.keys():
    greedy_mg5_growth_cap_df[f'{reactor}_new'] = greedy_mg5_growth_cap_df[f'num_{reactor}']

greedy_mg5_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../greedy/five/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_mg5_growth_cap_df, reactor)
    with open(f'{output_dir}mg5_greedy_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Rand + Greedy

greedy_mg5_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_mg5_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_mg5_growth_cap_df = greedy_mg5_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.rand_greedy_deployment(df=greedy_mg5_growth_cap_df, base_col='New Capacity Inc 1.0017440249087228', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year)

for reactor in sd.ad_reactors.keys():
    greedy_mg5_growth_cap_df[f'{reactor}_new'] = greedy_mg5_growth_cap_df[f'num_{reactor}']

greedy_mg5_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../rand_greed/five/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_mg5_growth_cap_df, reactor)
    with open(f'{output_dir}mg5_rand_greedy_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Random

greedy_mg5_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_mg5_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_mg5_growth_cap_df = greedy_mg5_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.rand_deployment(df=greedy_mg5_growth_cap_df, base_col='New Capacity Inc 1.0017440249087228', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year)

for reactor in sd.ad_reactors.keys():
    greedy_mg5_growth_cap_df[f'{reactor}_new'] = greedy_mg5_growth_cap_df[f'num_{reactor}']

greedy_mg5_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../random/five/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_mg5_growth_cap_df, reactor)
    with open(f'{output_dir}mg5_random_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# # 15% Growth by 2050

rate = 1.15**(1/(2050-2022))
print(f"Rate of growth: {rate}")

med_15_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=med_15_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

for reactor in sd.ad_reactors.keys():
    med_15_growth_cap_df[f'{reactor}'] = np.ceil(med_15_growth_cap_df[f'New Capacity Inc {rate}']/sd.ad_reactors[reactor][0])

for reactor in sd.ad_reactors.keys():
    med_15_growth_cap_df[f'{reactor}_new'] = med_15_growth_cap_df[f'{reactor}'].diff()

output_dir = '../single_reactor/one_fuel/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(med_15_growth_cap_df, reactor)
    with open(f'{output_dir}m15g_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)


# ## Greedy

greedy_mg15_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_mg15_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_mg15_growth_cap_df = greedy_mg15_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.greedy_deployment(df=greedy_mg15_growth_cap_df, base_col='New Capacity Inc 1.0050039762209513', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year)

for reactor in sd.ad_reactors.keys():
    greedy_mg15_growth_cap_df[f'{reactor}_new'] = greedy_mg15_growth_cap_df[f'num_{reactor}']

greedy_mg15_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../greedy/fifteen/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_mg15_growth_cap_df, reactor)
    with open(f'{output_dir}mg15_greedy_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Rand + Greedy

greedy_mg15_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_mg15_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_mg15_growth_cap_df = greedy_mg15_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.rand_greedy_deployment(df=greedy_mg15_growth_cap_df, base_col='New Capacity Inc 1.0050039762209513', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year, set_seed=True)

for reactor in sd.ad_reactors.keys():
    greedy_mg15_growth_cap_df[f'{reactor}_new'] = greedy_mg15_growth_cap_df[f'num_{reactor}']

greedy_mg15_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../rand_greed/fifteen/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_mg15_growth_cap_df, reactor)
    with open(f'{output_dir}mg15_rand_greedy_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Random

greedy_mg15_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_mg15_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_mg15_growth_cap_df = greedy_mg15_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.rand_deployment(df=greedy_mg15_growth_cap_df, base_col='New Capacity Inc 1.0050039762209513', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year, set_seed=True)

for reactor in sd.ad_reactors.keys():
    greedy_mg15_growth_cap_df[f'{reactor}_new'] = greedy_mg15_growth_cap_df[f'num_{reactor}']

greedy_mg15_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../random/fifteen/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_mg15_growth_cap_df, reactor)
    with open(f'{output_dir}mg15_random_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)




# # Double by 2050 starting in 2030

rate = 2**(1/(2050-2030))
print(f"Rate of growth: {rate}")

d_2_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=d_2_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

for reactor in sd.ad_reactors.keys():
    d_2_growth_cap_df[f'{reactor}'] = np.ceil(d_2_growth_cap_df[f'New Capacity Inc {rate}']/sd.ad_reactors[reactor][0])

for reactor in sd.ad_reactors.keys():
    d_2_growth_cap_df[f'{reactor}_new'] = d_2_growth_cap_df[f'{reactor}'].diff()

output_dir = '../single_reactor/one_fuel/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(d_2_growth_cap_df, reactor)
    with open(f'{output_dir}d2g_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Greedy

greedy_dg2_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_dg2_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_dg2_growth_cap_df = greedy_dg2_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.greedy_deployment(df=greedy_dg2_growth_cap_df, base_col='New Capacity Inc 1.0352649238413776', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year)

for reactor in sd.ad_reactors.keys():
    greedy_dg2_growth_cap_df[f'{reactor}_new'] = greedy_dg2_growth_cap_df[f'num_{reactor}']

greedy_dg2_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../greedy/double/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_dg2_growth_cap_df, reactor)
    with open(f'{output_dir}dg2_greedy_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Rand + Greedy

greedy_dg2_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_dg2_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_dg2_growth_cap_df = greedy_dg2_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.rand_greedy_deployment(df=greedy_dg2_growth_cap_df, base_col='New Capacity Inc 1.0352649238413776', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year, set_seed=True)

for reactor in sd.ad_reactors.keys():
    greedy_dg2_growth_cap_df[f'{reactor}_new'] = greedy_dg2_growth_cap_df[f'num_{reactor}']

greedy_dg2_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../rand_greed/double/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_dg2_growth_cap_df, reactor)
    with open(f'{output_dir}dg2_rand_greedy_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Random

greedy_dg2_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_dg2_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_dg2_growth_cap_df = greedy_dg2_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.rand_deployment(df=greedy_dg2_growth_cap_df, base_col='New Capacity Inc 1.0352649238413776', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year, set_seed=True)

for reactor in sd.ad_reactors.keys():
    greedy_dg2_growth_cap_df[f'{reactor}_new'] = greedy_dg2_growth_cap_df[f'num_{reactor}']

greedy_dg2_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../random/double/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_dg2_growth_cap_df, reactor)
    with open(f'{output_dir}dg2_random_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)




# # Triple by 2050 from 2030

rate = 3**(1/(2050-2030))
print(f"Rate of growth: {rate}")

d_3_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=d_3_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

for reactor in sd.ad_reactors.keys():
    d_3_growth_cap_df[f'{reactor}'] = np.ceil(d_3_growth_cap_df[f'New Capacity Inc {rate}']/sd.ad_reactors[reactor][0])

for reactor in sd.ad_reactors.keys():
    d_3_growth_cap_df[f'{reactor}_new'] = d_3_growth_cap_df[f'{reactor}'].diff()

output_dir = '../single_reactor/one_fuel/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(d_3_growth_cap_df, reactor)
    with open(f'{output_dir}d3g_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)




# ## Greedy

greedy_dg3_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_dg3_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_dg3_growth_cap_df = greedy_dg3_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.greedy_deployment(df=greedy_dg3_growth_cap_df, base_col='New Capacity Inc 1.056467308549538', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year)

for reactor in sd.ad_reactors.keys():
    greedy_dg3_growth_cap_df[f'{reactor}_new'] = greedy_dg3_growth_cap_df[f'num_{reactor}']

greedy_dg3_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../greedy/triple/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_dg3_growth_cap_df, reactor)
    with open(f'{output_dir}dg2_greedy_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)




# ## Rand + Greedy

greedy_dg3_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_dg3_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_dg3_growth_cap_df = greedy_dg3_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.rand_greedy_deployment(df=greedy_dg3_growth_cap_df, base_col='New Capacity Inc 1.056467308549538', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year, set_seed=True)

for reactor in sd.ad_reactors.keys():
    greedy_dg3_growth_cap_df[f'{reactor}_new'] = greedy_dg3_growth_cap_df[f'num_{reactor}']

greedy_dg3_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../rand_greed/triple/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_dg3_growth_cap_df, reactor)
    with open(f'{output_dir}dg2_rand_greedy_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)



# ## Random

greedy_dg3_growth_cap_df = capacity_change_df.copy()
dep.capacity_increase(df=greedy_dg3_growth_cap_df, base_col='Total LWR Capacity', rate=rate, start_year=sd.transition_year, end_year=sd.sim_end_yr)

# Make a column for the year.
greedy_dg3_growth_cap_df = greedy_dg3_growth_cap_df.reset_index().rename(columns={'index':'Year'})

dep.rand_deployment(df=greedy_dg3_growth_cap_df, base_col='New Capacity Inc 1.056467308549538', ar_dict=sd.ad_reactors, dep_start_year=sd.transition_year, set_seed=True)

for reactor in sd.ad_reactors.keys():
    greedy_dg3_growth_cap_df[f'{reactor}_new'] = greedy_dg3_growth_cap_df[f'num_{reactor}']

greedy_dg3_growth_cap_df.set_index('Year', inplace=True)

output_dir = '../random/triple/deployment_calcs/'
for reactor in sd.ad_reactors.keys():
    xml_string = generate_deployinst_xml(greedy_dg3_growth_cap_df, reactor)
    with open(f'{output_dir}dg2_random_{reactor}_deployinst.xml', 'w') as f:
        f.write(xml_string)
