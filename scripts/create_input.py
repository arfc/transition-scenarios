import numpy as np
import pandas as pd
import sys

import predicting_the_past_import as import_data


#use of file: python create_input.py  2019
#asumes file name and location, just input year of data

#csv_file = sys.argv[1]
data_year = sys.argv[1]

#read in csv, remove first 2 columns
reactor_data = pd.read_csv('../database/Year-end Reactor Status.csv')
reactor_data = reactor_data.drop


# Different file path variables
region = 'united_states'
pris_file = '../database/reactors_pris_2016.csv'
deployinst_tmpl = '../input/predicting-the-past/templates/' + region + '/deployinst_template.xml'
inclusions_tmpl = '../input/predicting-the-past/templates/inclusions_template.xml'
pris = import_data.import_csv('../database/reactors_pris_2016.csv', ',')

deployment_path = '../input/haleu/input/' + region + '/buildtimes'
reactor_path = '../input/haleu/input/' + region + '/reactors'
reactor_template = '../input/predicting-the-past/templates/reactors_template.xml'
#Pulled from united_states.ipynb

recipes = import_data.import_csv('../database/vision_recipes/uox.csv', ',')

recipe_template = import_data.load_template('../input/predicting-the-past/templates/recipes_template.xml')

fresh33 = import_data.get_composition_fresh(recipes, 33)
spent33 = import_data.get_composition_spent(recipes, 33)
fresh51 = import_data.get_composition_fresh(recipes, 51)
spent51 = import_data.get_composition_spent(recipes, 51)
fresh100 = import_data.get_composition_fresh(recipes, 100)
spent100 = import_data.get_composition_spent(recipes, 100)

import_data.write_recipes(fresh33, spent33, recipe_template, 33, region)
import_data.write_recipes(fresh51, spent51, recipe_template, 51, region)
import_data.write_recipes(fresh51, spent51, recipe_template, 100, region)

reactor_list = import_data.select_region(pris, 'UNITED_STATES')

import_data.write_reactors(reactor_list, reactor_path, reactor_template,18,1) # change cycle and refuel time 

buildtime = import_data.deploy_reactors(pris_file, region, 1965, deployinst_tmpl,
                            inclusions_tmpl, reactor_path, deployment_path)

cyclus_tmpl = ('../input/predicting-the-past/templates/' + region + '/' + region + '_template.xml')
import_data.render_cyclus(cyclus_tmpl, region, buildtime, '../input/haleu/input/',51) # change burn up 
