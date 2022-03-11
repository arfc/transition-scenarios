## Templates folder
This directory contains templates that are used in the ```write_reactors``` 
function of ```scripts/predicting_the_past_import.py```.

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
