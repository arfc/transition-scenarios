# transition-scenarios

## Input Folder
The input folder is to generate various input files for transition scenario
simulations. Currently it has files that generate PWR input files with 
different capacities. The assumptions for the parameters are as follows:

	Cycle 		= 18 months (timesteps) for all
	Refueling 	= 2 months (timesteps) for all
	assembly mass 	= 180 UO2 / assembly for BWRs
			  523.4 UO2 / assembly for rest (PWR, nucleartourist.com)
	#of assemblies 	= 193 for 1000MWe, linearly adjusted for other capacities



### write_reactors.py
Python script for Cyclus input file generation.

This script allows generation of cyclus input file types from csv files.

Input : csv file, template for reactor input, template for region


	    
    csv_file: the csv file containing reactor name, capacity and
              the appropriate number of assemblies per core and per batch
	      
    reator_template: input file name for jinja template for cyclus reactor input
    
    deployinst_template: input file name for jinja template for cyclus region input
    
    input_template: input file template for a complete input file
    
    ractor_output: output file name for cyclus reactor input file
    
    region_output: output file name for cyclus region input file
    
    
Output : two input file blocks (reactor and region) for cyclus 
simulation, and a complete input file ready for simulation.
    
    
To run:

	python write_reactors.py [csv_file] [reactor_template] [deployinst_template]
				 [input_template] [reactor_output] [region_output]


### input_template.xml.in
