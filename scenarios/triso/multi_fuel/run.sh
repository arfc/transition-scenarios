# Xe100 = 1
# MMR = 2
# AP = 3

# No Growth
cyclus -v 3 -i dan1.xml -o output/dan1_out.sqlite >> output/dan1_out.log ;

cyclus -v 3 -i dan2.xml -o output/dan2_out.sqlite >> output/dan2_out.log ;

cyclus -v 3 -i dan3.xml -o output/dan3_out.sqlite >> output/dan3_out.log ;


# Low Growth
cyclus -v 3 -i dal1.xml -o output/dal1_out.sqlite >> output/dal1_out.log ;

cyclus -v 3 -i dal2.xml -o output/dal2_out.sqlite >> output/dal2_out.log ;

cyclus -v 3 -i dal3.xml -o output/dal3_out.sqlite >> output/dal3_out.log ;


# Medium Growth
cyclus -v 3 -i da5l1.xml -o output/da5l1_out.sqlite >> output/da5l1_out.log ;

cyclus -v 3 -i da5l2.xml -o output/da5l2_out.sqlite >> output/da5l2_out.log ;

cyclus -v 3 -i da5l3.xml -o output/da5l3_out.sqlite >> output/da5l3_out.log ;

cyclus -v 3 -i da15l1.xml -o output/da15l1_out.sqlite >> output/da15l1_out.log ;

cyclus -v 3 -i da15l2.xml -o output/da15l2_out.sqlite >> output/da15l2_out.log ;

cyclus -v 3 -i da15l3.xml -o output/da15l3_out.sqlite >> output/da15l3_out.log ;


# DOE report Growth
cyclus -v 3 -i da2d1.xml -o output/da2d1_out.sqlite >> output/da2d1_out.log ;

cyclus -v 3 -i da2d2.xml -o output/da2d2_out.sqlite >> output/da2d2_out.log ;

cyclus -v 3 -i da2d3.xml -o output/da2d3_out.sqlite >> output/da2d3_out.log ;


cyclus -v 3 -i da3d1.xml -o output/da3d1_out.sqlite >> output/da3d1_out.log ;

cyclus -v 3 -i da3d2.xml -o output/da3d2_out.sqlite >> output/da3d2_out.log ;

cyclus -v 3 -i da3d3.xml -o output/da3d3_out.sqlite >> output/da3d3_out.log ;


python plot_xe.py
