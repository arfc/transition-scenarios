# Global Sensitivity Analysis
This directory contains files for performing global sensitivity 
analysis on the transtion from US LWRs to advanced reactors. 
There are three subdirectories, one for varying the build share 
of each advanced reactor considered in this work. In each case 
(i.e., subdirectory) the transition start time, LWR lifetime, 
Xe-100 burnup, and MMR build share are varied, but the build share 
of only advanced reactor is varied. The build share of only 
one advanced reactor is varied at a time to prevent unphysical 
combinations of advanced reactor build shares (e.g., 50% Xe-100, 
50% MMR, and 50% VOYGR). 

Each subdirectory contains two different Dakota input files:
``list_sample.in`` and ``dakota.in``. The ``list_sample.in`` file 
treats the MMR burnup as a continuous variable and the Xe-100 
burnup as a discrete variable, with more points than previously 
considered. This input file is run first, creating a ``.dat`` file 
with data for the output metrics for each combination of input 
parameters. This ``.dat`` file is then read by the ``dakota.in`` 
input file to create a surrogate model of the data that treats all
of the variables as continuous. The suurogate models created by 
the ``dakota.in`` file are used for variance decomposition to 
calculate Sobol' indices. Two surrogate model fits are used: quadratic 
and gaussian. 
