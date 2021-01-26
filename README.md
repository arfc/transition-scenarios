# transition-scenarios

## Script directory
The script directory contains scripts that can be used to generate CYCLUS
input files and analyze CYCLUS output files.

### analysis.py

Input : CYCLUS output file (.sqlite)  
```
python analysis.py [outputfile]
```

Most functions return a dictionary of lists (timeseries of a value)
that can be used to plot a stacked bar chart or a line plot.

### create_input.py
Python script to create CYCLUS input files from PRIS Year-end Reator Status 
Reports. Once the Report is downloaded from the PRIS Database, it must be 
saved as ``database/Year-end Reactor Status_####.csv``, in which the ``####``
is the four digit year the data is pulled from. Creates multiple files that 
are used for a CYCLUS simulation, using functions contained in 
``predicting_the_past_import.py``. Due to relative path dependancies in this 
script, it **must** be run from the ``scripts`` directory.

Input : None

User Specifications : 
- l. 7 : ``data_year`` (int) -- four digit year the data is pulled from, must match 
the year in the Year-end Reactor Status file
- l. 8 : ``start_year`` (int) -- four digit year for the simulation to start on. The 
simulation will start in January of that year
- l. 9 : ``region`` (str) -- Region to include reactors from. Possible regions are 
Asia, United States, Europe, South America, North America, Africa, and All
Currently, only one region can be accepted at a time
- l. 10 : ``project`` (str) -- directory name in ``/input/`` to contain all of the CYCLUS
input files created
- l. 35 : ``burnup`` (list of ints) -- list of burnup values to be used in CYCLUS simulation. 
- l. 46 : cycle length of reactors (int) -- input to ``import_data.write_reactors()``
- l. 47 : refueling length of reactor (int) -- input to ``import_data.write_reactors()``
- l. 58 : simulation duration (int) -- duration of simulation in months; dafault value of 
780 months (65 years)
- l. 58 : burnup of reactors in CYCLUS simulation (int) -- must be a value in ``burnups``,
so that recipe files are present; default of 50 GWd/MTU


Outputs : 
- ``database/reactors_pris_####.csv`` : ``.csv`` file of condensed PRIS year-end Reactor 
Status information, in which ``####`` is the four digit year the data is pulled from
- ``input/project/inputs/region.xml`` : CYCLUS input file, in which ``project`` and ``region`` 
are user specifications
- ``input/project/inputs/region/recipes/`` : directory containing recipe files that are read into 
the CYCLUS input file, in which ``project`` and ``region`` are user specifications
- ``input/project/inputs/region/reactors'`` : directory containing input files for each of the 
reactors in the selected region. Each reactor will be a separate ``.xml`` input file that 
will be read into the CYCLUS input file, in which ``project`` and ``region`` are user 
specifications
- ``input/project/inputs/region/buildtimes/inclusions.xml`` : Input file that contains links
to the reactors in the region to be included in the CYLCUS simulation, in which ``project`` 
and ``region`` are user specifications
- ``input/project/inputs/region/buildtimes/country/deployinst.xml`` : Input file of the 
``DeployInst`` institution for the specified ``country`` that is read into the CYCLUS 
input file, in which ``project`` and ``region`` are user specifications

To run:
```
python create_input.py
```

### merge_coordinates.py
Reads in a PRIS data base, adds columns for the latitude and longitude for each 
reactor with available data from the coordinates database. Reactors that do not 
have available coordinates are left blank. The available database is 
``database/coordinates.sqlite``

To run:
```
python merge_coordinates.py [pris_link] [webscrape_link]
```
Inputs: 
- ``pris_link``: ``.csv`` file of raw reactor data
- ``webscrape_link``: SQLite data base of coordinates of reactor locations 

Outputs: 
- ``reactors_pris_2016.csv`` : ``.csv`` file of reactor data, including the latitude and 
longitude coordinates

### predicting_the_past_import.py
Contains functions used to create ``.xml`` input files for a CYCLUS simulation.  

To run:
``` 
python predicting_the_past.py
```
Inputs: None

Outputs: None

### random_lifetime_extensions.py
Function to apply lifetime extensions to reactors in a CYCLUS input, based on a Gaussian 
distribution (mean = 10, standard deviation = 3 years). 

To run:
```
python random_lifetime_extensions.py
```
Inputs: None

Outputs: None

### tests/test.sqlite
Simple Cyclus output for testing purposes.

### tests/test_analysis.py
testfile for analysis.py.  
To run:  
```
python test_analysis.py
```

### transition_plots.py
Functions to plot agents and undersupply of commodities for a CYCLUS simulation

To run:
```
python transition_plots.py
```
Inputs: None

Outputs: None

## Templates folder
This directory contains templates that are used in the write_reactors.py script.

### deployinst_template.xml.in
Jinja template for the individual region prototype of the cyclus input file.

### inclusions_template.xml.in
Jinja template for the reactor input files to include in the simulation

### reactor_template.xml.in
Jinja template for the reactor section of the cyclus input file.

### reciptes_template.xml.in
Jinja template for the recipe section of the cyclus input file. 

### united_states_template.xml.in
Jinja Template for the entire Cyclus input file of the United States fuel cycle.

This is where the compiled reactor and region files will be rendered into.

fuel composition data is from representative vision recipes.

## Database folder
### coordinates.sqlite
Database of latitude and longitude coordinatates of reactors in the PRIS
database

### deploy_schedule.xml
This file contains various deployment schedules for transition
scenarios (EG01 - EG 23, 24, 29, 30). The simulation starts
at 100 GWe of LWR installed capacity in 2015. The simulation
is 200 years long and an annual growth of 1% is assumed. The
new reactor types (or fuel cycles) are available from 2050.

### vision_recipes/ 
directory of ``.csv`` files for various uox and mox fuel recipes, both fresh 
and spent fuel

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
under input/ directory

## REPORT
To view the the report which includes the procedure, results and their
explanations, please view `united_states.ipynb` or `europe.ipynb`.

## Not Ready For Reuse
During development, this work is under sole development by the authors in
preparation for publication in conference proceedings or an archival journal.
