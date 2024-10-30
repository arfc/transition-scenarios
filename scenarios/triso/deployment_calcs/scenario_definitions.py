# This file contains the definitions for the scenario calculations as shared
# variables for the deployment calculations.
sim_start_yr = 1958
sim_end_yr = 2105

# assume capacity factor for LWRs is the same, and constant
lwr_capacity_factor = 0.925  # [%]

# Assumes that reactors are deployed after the transition_year, if the reactor
# starts in 2030, you would put 2029.
transition_year = 2029  # [yr]

# define each reactor individually, in order from most power to least (the
# functions rely on this)
ad_reactors = {'AP1000':[1117, 0.925, 80, 'no_dist'],'Xe100': [80, 1, 60, 'no_dist'], 'MMR': [5, 1, 20, 'no_dist']}
# {reactor: [Power (MWe), capacity_factor (%), lifetime (yr), distribution
# (default='no_dist')]}
