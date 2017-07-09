# transition-scenarios

## Script Folder
The script folder contains scripts that can be used to generate CYCLUS
input files and analyze CYCLUS output files.


### write_reactors.py
Python script for CYCLUS input file generation.

The assumptions for the parameters are as follows:

	Cycle 		= 18 months (timesteps) for all
	Refueling 	= 2 months (timesteps) for all
	assembly mass 	= 180 UO2 / assembly for BWRs
			  		  523.4 UO2 / assembly for rest [PWR](nucleartourist.com)
	#of assemblies 	= 193 for 1000MWe, linearly adjusted for other capacities

This script allows generation of CYCLUS input file types from csv files.

Input : csv file, initial_time, duration, reprocessing 


	    
    csv_file: the csv file containing country, reactor name and capacity
    
    initial_time: initial time of the simulation in yyyymmdd

    duration: duration of the simulation in months
    
    
Output : A complete input file ready for simulation. (default: complete_input.xml)
    
To run:

	python write_reactors.py [csv_file] [init_time] [duration]


### analysis.py

Input : CYCLUS output file (.sqlite)
`python analysis.py [outputfile]`

Most functions return a dictionary of lists (timeseries of a value)
that can be used to plot a stacked bar chart or a line plot.

Major analysis functions include:
1. commodity_in_out_facility
Returns dictionary of influx/outflux of a commodity from a facility.

2.  get_stockpile
Returns dictionary of stockpile in a fuel cycle facility.

3. get_swu_dict
Returns dictionary of swu timeseries for each enrichment plant.

4. fuel_usage_timeseries
Returns dictionary of timeseries of fuel used in simulation.

5. get_trade_dict
Returns dictionary of trade timeseries between two prototype/specs.

6. u_util_calc
Returns dictionary of timeseries of uranium utilization factor (fuel/natu_supply).

7. where_comm
Returns dictionary of timeseries of a commodity separated by its origin.

8. plot_power
Returns dictionary of timeseries of number of reactors & installed capacity.


The Returned Dictionaries can be used to build plots:
1. stacked_bar_chart
stacked bar chart (every key in dictionary is plotted on top of each other)

2. multi_line_plot
creates separate line plot for each key in dictionary.


## Templates Folder
This folder contains templates that are used in the write_reactors.py script.

### input_template.xml.in
Jinja Template for the entire Cyclus input file.

This is where the compiled reactor and region files will be rendered into.

fuel composition data is from representative vision recipes.

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

