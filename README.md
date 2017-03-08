# transition-scenarios

## Input Folder
The input folder is to generate various input files for transition scenario
simulations. Currently it has files that generate PWR input files with 
different capacities. The assumptions for the parameters are as follows:

	Cycle 			= 18 months (timesteps) for all
	Refueling 		= 2 months (timesteps) for all
	assembly mass 	= 523.4 UO2 / assembly for all (PWR, nucleartourist.com)
	#of assemblies 	= 193 for 1000MWe, linearly adjusted for other capacities



### write_reactors.py
Python script for Cyclus input file generation.

This script allows generation of cyclus input file types from csv files.

Input : csv file, template for reactor input, template for region


	    
    csv_file: the csv file containing reactor name, capacity and
              the appropriate number of assemblies per core and per batch
	      
    reator_template: input file name for jinja template for cyclus reactor input
    
    region_template: input file name for jinja template for cyclus region input
    
    input_template: input file template for a complete input file
    
    ractor_output: output file name for cyclus reactor input file
    
    region_output: output file name for cyclus region input file
    
    
Output : two input file blocks (reactor and region) for cyclus 
simulation, and a complete input file ready for simulation.
    
    
To run:

	python write_reactors.py [csv_file] [reactor_template] [region_template]
				 [input_template] [reactor_output] [region_output]


### input_template.xml.in
Jinja Template for the entire Cyclus input file.

This is where the compiled reactor and region files will be rendered into.

### reactor_template.xml.in
Jinja template for the reactor section of the cyclus input file.

### region_template.xml.in
Jinja template for the individual region prototype of the cyclus input file.

### region_output_template.xml.in
Jinja template for the region section of the cylcus input file.

Grouped region prototypes will be rendered into this file.


## Europe Folder
The eu.csv file lists all the nuclear reactors in europe.
The data is from a [wikipedia page](https://en.wikipedia.org/wiki/List_of_nuclear_reactors)
and is converted to a csv file using an
[external website](http://wikitable2csv.ggor.de/).

The csv file lists the following:
* Reactor Name
* Unit Number
* Reactor Type / Model
* Status
* Net / Gross Capacity
* Construction Start Date
* Commercial Operation Date
* Closure (if applicable)

The other csv files in the folder are trimmed-down versions
for the write_reactors.py file.
