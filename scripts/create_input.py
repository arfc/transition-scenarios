import pandas as pd
import sys

import predicting_the_past_import as import_data

# user defined characteristics of cyclus simulation
data_year = 2019
start_year = 1965
region = 'united_states'
project = 'haleu'

reactor_data = import_data.import_pris('../database/Year-end Reactor Status_' + str(data_year) +'.csv')
reactor_data = reactor_data[reactor_data.Unit.notnull()]
reactor_data = reactor_data[reactor_data.Unit != 'Unit']
reactor_data = reactor_data.rename(columns= {'ARGENTINA':'Country'})
import_data.save_output(reactor_data, data_year)


pris_file = '../database/reactors_pris_' + str(data_year) + '.csv'
deployinst_tmpl = '../input/predicting-the-past/templates/' + region + '/deployinst_template.xml'
inclusions_tmpl = '../input/predicting-the-past/templates/inclusions_template.xml'
deployment_path = '../input/' + project + '/inputs/' + region + '/buildtimes'
reactor_path = '../input/' + project + '/inputs/' + region + '/reactors'
reactor_template = '../input/predicting-the-past/templates/reactors_template.xml'


pris = import_data.import_csv(pris_file)


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

reactor_list = import_data.select_region(pris, region)
import_data.write_reactors(reactor_list, reactor_path, reactor_template,18,1) # change cycle and refuel time 
buildtime = import_data.deploy_reactors(pris_file, region, start_year, deployinst_tmpl,
                            inclusions_tmpl, reactor_path, deployment_path)

cyclus_tmpl = ('../input/predicting-the-past/templates/' + region + '/' + region + '_template.xml')
import_data.render_cyclus(cyclus_tmpl, region, buildtime, '../input/' + project + '/inputs/',51) # change burn up 
