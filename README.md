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
Jinja Template for the entire Cyclus input file.

This is where the compiled reactor and region files will be rendered into.

### reactor_template.xml.in
Jinja template for the reactor section of the cyclus input file.

### deployinst_template.xml.in
Jinja template for the individual region prototype of the cyclus input file.

### region_output_template.xml.in
Jinja template for the region section of the cylcus input file.

### somesource_sink.xml.in
text file containing NullInst with SomeSource and Somesink

Grouped region prototypes will be rendered into this file.


## Europe Folder

# eu_reactors_pris.csv
The eu_reactors_pris.csv file lists all the nulear reactors in europe,
but more in detail. The data is from [PRIS - IAEA](https://www.iaea.org/pris/)
and is converted to as csv file.

The csv file lists the following :
* Country
* Reactor Unit (name)
* Type
* Net Capacity (MWe)
* Status
* Operator
* Construction date
* Construction year
* First criticality date
* Two empty columns for start / end date (for deployinst)
* First grid date
* Commercial date
* Shutdown date
* UCF (Unit Capacity Factor) for 2013 (in %)


## output folder
The output folder contains analysis tools for cylcus output files.

### analysis.py
Does simple analysis of cyclus input file, prints snf inventory mass
and shows stacked bar chart of net capacity over time.
Usage: ` python anaylsis.py [cylcus_output_file]

