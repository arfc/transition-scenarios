[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Predicting the Past Cyclus and Cycamore Benchmarking Project
==============================================================

This is a public repository for the shared development of benchmarking
simulation input data representing the past nuclear fuel cycle in the united
states. It is being conducted by undergraduate researchers at the University of
Illinois at Urbana-Champaign in the Advanced Reactors and Fuel Cycles group.
This work benefits enormously from previous work by Robert Flanagan in the
fleetcomp repository.

Not Ready For Reuse
====================

During development, this work is under sole development by the authors in
preparation for publication in conference proceedings or an archival journal.

Generating Cycamore Reactor input
=================================

Cycamore reactor input and its in_commod and out_commod recipies are produced
from the 'US_Fleet.txt' file and 'vision_recipes.xls' file.

Usage:
1. python recipe_generator.py [InputData] [TemplateFile]

Example (Natively available on Ubuntu):

    python recipe_generator.py fleetcomp/US_Fleet.txt templates/template.xml

How to include xml files within an xml file
===========================================

To include a xml file (i.e. a.xml) into another xml (i.e. b.xml) file, add xinclude
in the xml namespace by adding the following to the root tag:

    xmlns:xi="http://www.w3.org/2001/XInclude"

Then, reference the xml that needs to be added (a.xml) into the appropriate level
with the line:

    <xi:include href="[path_to_a.xml/a.xml]" />

Unless the xml parser natively supports xinclude, the resulting xml file may have
to be parsed with a parser that supports xinclude. An xml parsing script with
xinclude support is provided in the repository. Refer to the files in this
repository for example.