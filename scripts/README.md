## Script directory
This directory contains scripts that can be used to generate CYCLUS
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

### tests/test_transition_metrics.py
testfile for transition_metrics.py.  
To run:  
```
pytest test_transition_metrics.py
```

### tests/transition_metrics_decommission_test.py
testfile for transition_metrics, with the simulation 
designed to have facilities decommissioned.  

### tests/transition_metrics_nodecommission_test.py
testfile for transition_metrics, with the simulation 
designed to not have facilities decommissioned. 


### transition_metrics.py
Functions to plot and analyze data for the results in ```input/haleu```. 

To run:
```
python transition_metrics.py
```
Inputs: None

Outputs: None

### transition_plots.py
Functions to plot agents and undersupply of commodities for a CYCLUS simulation

To run:
```
python transition_plots.py
```
Inputs: None

Outputs: None

