########################################
############ Single Reactor ############
########################################


################
### One Fuel ###
################
# No Growth
cyclus -v 3 -i single_reactor/one_fuel/dan1.xml -o single_reactor/one_fuel/output/dan1_out.sqlite >> single_reactor/one_fuel/output/dan1_out.log ;

cyclus -v 3 -i single_reactor/one_fuel/dan2.xml -o single_reactor/one_fuel/output/dan2_out.sqlite >> single_reactor/one_fuel/output/dan2_out.log ;

cyclus -v 3 -i single_reactor/one_fuel/dan3.xml -o single_reactor/one_fuel/output/dan3_out.sqlite >> single_reactor/one_fuel/output/dan3_out.log ;


# Low Growth
cyclus -v 3 -i single_reactor/one_fuel/dal1.xml -o single_reactor/one_fuel/output/dal1_out.sqlite >> single_reactor/one_fuel/output/dal1_out.log ;

cyclus -v 3 -i single_reactor/one_fuel/dal2.xml -o single_reactor/one_fuel/output/dal2_out.sqlite >> single_reactor/one_fuel/output/dal2_out.log ;

cyclus -v 3 -i single_reactor/one_fuel/dal3.xml -o single_reactor/one_fuel/output/dal3_out.sqlite >> single_reactor/one_fuel/output/dal3_out.log ;


# Medium Growth
cyclus -v 3 -i single_reactor/one_fuel/da5l1.xml -o single_reactor/one_fuel/output/da5l1_out.sqlite >> single_reactor/one_fuel/output/da5l1_out.log ;

cyclus -v 3 -i single_reactor/one_fuel/da5l2.xml -o single_reactor/one_fuel/output/da5l2_out.sqlite >> single_reactor/one_fuel/output/da5l2_out.log ;

cyclus -v 3 -i single_reactor/one_fuel/da5l3.xml -o single_reactor/one_fuel/output/da5l3_out.sqlite >> single_reactor/one_fuel/output/da5l3_out.log ;

cyclus -v 3 -i single_reactor/one_fuel/da15l1.xml -o single_reactor/one_fuel/output/da15l1_out.sqlite >> single_reactor/one_fuel/output/da15l1_out.log ;

cyclus -v 3 -i single_reactor/one_fuel/da15l2.xml -o single_reactor/one_fuel/output/da15l2_out.sqlite >> single_reactor/one_fuel/output/da15l2_out.log ;

cyclus -v 3 -i single_reactor/one_fuel/da15l3.xml -o single_reactor/one_fuel/output/da15l3_out.sqlite >> single_reactor/one_fuel/output/da15l3_out.log ;


# DOE report Growth
cyclus -v 3 -i single_reactor/one_fuel/da2d1.xml -o single_reactor/one_fuel/output/da2d1_out.sqlite >> single_reactor/one_fuel/output/da2d1_out.log ;

cyclus -v 3 -i single_reactor/one_fuel/da2d2.xml -o single_reactor/one_fuel/output/da2d2_out.sqlite >> single_reactor/one_fuel/output/da2d2_out.log ;

cyclus -v 3 -i single_reactor/one_fuel/da2d3.xml -o single_reactor/one_fuel/output/da2d3_out.sqlite >> single_reactor/one_fuel/output/da2d3_out.log ;


cyclus -v 3 -i single_reactor/one_fuel/da3d1.xml -o single_reactor/one_fuel/output/da3d1_out.sqlite >> single_reactor/one_fuel/output/da3d1_out.log ;

cyclus -v 3 -i single_reactor/one_fuel/da3d2.xml -o single_reactor/one_fuel/output/da3d2_out.sqlite >> single_reactor/one_fuel/output/da3d2_out.log ;

cyclus -v 3 -i single_reactor/one_fuel/da3d3.xml -o single_reactor/one_fuel/output/da3d3_out.sqlite >> single_reactor/one_fuel/output/da3d3_out.log ;


##################
### Multi Fuel ###
##################

# No Growth
cyclus -v 3 -i single_reactor/multi_fuel/dan1.xml -o single_reactor/multi_fuel/output/dan1_out.sqlite >> single_reactor/multi_fuel/output/dan1_out.log ;

cyclus -v 3 -i single_reactor/multi_fuel/dan2.xml -o single_reactor/multi_fuel/output/dan2_out.sqlite >> single_reactor/multi_fuel/output/dan2_out.log ;


# Low Growth
cyclus -v 3 -i single_reactor/multi_fuel/dal1.xml -o single_reactor/multi_fuel/output/dal1_out.sqlite >> single_reactor/multi_fuel/output/dal1_out.log ;

cyclus -v 3 -i single_reactor/multi_fuel/dal2.xml -o single_reactor/multi_fuel/output/dal2_out.sqlite >> single_reactor/multi_fuel/output/dal2_out.log ;


# Medium Growth
cyclus -v 3 -i single_reactor/multi_fuel/da5l1.xml -o single_reactor/multi_fuel/output/da5l1_out.sqlite >> single_reactor/multi_fuel/output/da5l1_out.log ;

cyclus -v 3 -i single_reactor/multi_fuel/da5l2.xml -o single_reactor/multi_fuel/output/da5l2_out.sqlite >> single_reactor/multi_fuel/output/da5l2_out.log ;


cyclus -v 3 -i single_reactor/multi_fuel/da15l1.xml -o single_reactor/multi_fuel/output/da15l1_out.sqlite >> single_reactor/multi_fuel/output/da15l1_out.log ;

cyclus -v 3 -i single_reactor/multi_fuel/da15l2.xml -o single_reactor/multi_fuel/output/da15l2_out.sqlite >> single_reactor/multi_fuel/output/da15l2_out.log ;


# DOE report Growth
cyclus -v 3 -i single_reactor/multi_fuel/da2d1.xml -o single_reactor/multi_fuel/output/da2d1_out.sqlite >> single_reactor/multi_fuel/output/da2d1_out.log ;

cyclus -v 3 -i single_reactor/multi_fuel/da2d2.xml -o single_reactor/multi_fuel/output/da2d2_out.sqlite >> single_reactor/multi_fuel/output/da2d2_out.log ;


cyclus -v 3 -i single_reactor/multi_fuel/da3d1.xml -o single_reactor/multi_fuel/output/da3d1_out.sqlite >> single_reactor/multi_fuel/output/da3d1_out.log ;

cyclus -v 3 -i single_reactor/multi_fuel/da3d2.xml -o single_reactor/multi_fuel/output/da3d2_out.sqlite >> single_reactor/multi_fuel/output/da3d2_out.log ;


#################################
############ Greedy #############
#################################

# No Growth
cyclus -v 3 -i greedy/ng/dgng.xml -o greedy/ng/output/dgng_out.sqlite >> greedy/ng/output/dgng_out.log ;


# Low Growth
cyclus -v 3 -i greedy/one/dg1.xml -o greedy/one/output/dg1_out.sqlite >> greedy/one/output/dg1_out.log ;


# Medium Growth

cyclus -v 3 -i greedy/five/dg5.xml -o greedy/five/output/dg5_out.sqlite >> greedy/five/output/dg5_out.log ;

cyclus -v 3 -i greedy/fifteen/dg15.xml -o greedy/fifteen/output/dg15_out.sqlite >> greedy/fifteen/output/dg15_out.log ;


# DOE report Growth

cyclus -v 3 -i greedy/double/dg2.xml -o greedy/double/output/dg2_out.sqlite >> greedy/double/output/dg2_out.log ;

cyclus -v 3 -i greedy/double/dg3.xml -o greedy/double/output/dg3_out.sqlite >> greedy/double/output/dg3_out.log ;


#################################
############# Random ############
#################################

# No Growth
cyclus -v 3 -i random/ng/drng.xml -o random/ng/output/drng_out.sqlite >> random/ng/output/drng_out.log ;


# Low Growth
cyclus -v 3 -i random/one/dr1.xml -o random/one/output/dr1_out.sqlite >> random/one/output/dr1_out.log ;


# Medium Growth
cyclus -v 3 -i random/five/dr5.xml -o random/five/output/dr5_out.sqlite >> random/five/output/dr5_out.log ;

cyclus -v 3 -i random/fifteen/dr15.xml -o random/fifteen/output/dr15_out.sqlite >> random/fifteen/output/dr15_out.log ;


# DOE report Growth

cyclus -v 3 -i random/double/dr2.xml -o random/double/output/dr2_out.sqlite >> random/double/output/dr2_out.log ;

cyclus -v 3 -i random/double/dr3.xml -o random/double/output/dr3_out.sqlite >> random/double/output/dr3_out.log ;



########################################
########### Random + Greedy ############
########################################

# No Growth
cyclus -v 3 -i rand_greed/ng/drgng.xml -o rand_greed/ng/output/drgng_out.sqlite >> rand_greed/ng/output/drgng_out.log ;


# Low Growth
cyclus -v 3 -i rand_greed/one/drg1.xml -o rand_greed/one/output/drg1_out.sqlite >> rand_greed/one/output/drg1_out.log ;


# Medium Growth
cyclus -v 3 -i rand_greed/five/drg5.xml -o rand_greed/five/output/drg5_out.sqlite >> rand_greed/five/output/drg5_out.log ;

cyclus -v 3 -i rand_greed/fifteen/drg15.xml -o rand_greed/fifteen/output/drg15_out.sqlite >> rand_greed/fifteen/output/drg15_out.log ;


# DOE report Growth
cyclus -v 3 -i rand_greed/double/drg2.xml -o rand_greed/double/output/drg2_out.sqlite >> rand_greed/double/output/drg2_out.log ;

cyclus -v 3 -i rand_greed/double/drg3.xml -o rand_greed/double/output/drg3_out.sqlite >> rand_greed/double/output/drg3_out.log ;