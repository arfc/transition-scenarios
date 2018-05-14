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
```
python analysis.py [outputfile]
```

Most functions return a dictionary of lists (timeseries of a value)
that can be used to plot a stacked bar chart or a line plot.


### test.sqlite
Simple Cyclus output for testing purposes.

### test_analysis.py
testfile for analysis.py.  
To run:  
```
python test_analysis.py
```

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

### eu_reactors_pris.csv
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

### deploy_schedule.xml
This file contains various deployment schedules for transition
scenarios (EG01 - EG 23, 24, 29, 30). The simulation starts
at 100 GWe of LWR installed capacity in 2015. The simulation
is 200 years long and an annual growth of 1% is assumed. The
new reactor types (or fuel cycles) are available from 2050.

## scenario_specification.md
This file contains specific details about the transition
scenarios such as fuel mass, composition, and refueling
cycles. The file also identifies some gaps in the current
CYCLUS regarding transition scenarios.
=======
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)


# Predicting the Past Cyclus and Cycamore Benchmarking Project
This is a public repository for the shared development of benchmarking
simulation input data representing the past nuclear fuel cycle in the United 
States and Europe. It is being conducted by undergraduate researchers at the 
University of Illinois at Urbana-Champaign in the Advanced Reactors and Fuel
Cycles group.

To view the work or run a simulation for a particular region, open [region_name].ipynb
under input/ folder

## REPORT
To view the the report which includes the procedure, results and their
explanations, please view `united_states.ipynb` or `europe.ipynb`.

## Not Ready For Reuse
During development, this work is under sole development by the authors in
preparation for publication in conference proceedings or an archival journal.