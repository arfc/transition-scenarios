# transition-scenarios

## Script Folder
The script folder contains scripts that can be used to generate cyclus
input files and anaylse cyclus output files.




### write_reactors.py
Python script for Cyclus input file generation.

The assumptions for the parameters are as follows:

	Cycle 		= 18 months (timesteps) for all
	Refueling 	= 2 months (timesteps) for all
	assembly mass 	= 180 UO2 / assembly for BWRs
			  		  523.4 UO2 / assembly for rest [PWR](nucleartourist.com)
	#of assemblies 	= 193 for 1000MWe, linearly adjusted for other capacities

This script allows generation of cyclus input file types from csv files.

Input : csv file, initial_time, duration, reprocessing 


	    
    csv_file: the csv file containing country, reactor name and capacity
    
    initial_time: initial time of the simulation in yyyymmdd

    duration: duration of the simulation in months
    
    
Output : A complete input file ready for simulation. (default: complete_input.xml)
    
To run:

	python write_reactors.py [csv_file] [init_time] [duration]


### analysis.py
Script that can be used to:
1. print total snf amount and isotope mass (analysis.snf(cursor))
2. create stacked bar chart of power capacity and number of reactors per region (analysis.plot_power(cursor))
3. create a multi-line plot chart of waste isotope per time (analysis.isotope_vs_time(cursor))

The following command on the terminal will execute all three:

`python anaylsis.py [cylcus_output_file]`


## Templates Folder
This folder contains templates that are used in the write_reactors.py script.

### input_template.xml.in
Jinja Template for the entire Cyclus input file.

This is where the compiled reactor and region files will be rendered into.

fuel composition data is from an ORIGEN calculation (not public data)

### reactor_template.xml.in
Jinja template for the reactor section of the cyclus input file.

### reactor_mox_template.xml.in
Jinja tempalte for reactors that use mox

### deployinst_template.xml.in
Jinja template for the individual region prototype of the cyclus input file.

### region_output_template.xml.in
Jinja template for the region section of the cylcus input file.

Grouped region prototypes will be rendered into this file.


## Database Folder

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

