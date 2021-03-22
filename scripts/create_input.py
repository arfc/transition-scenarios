import pandas as pd
import sys

import predicting_the_past_import as import_data
# module containing functions to build CYCLUS input file

# user defined characteristics of cyclus simulation
data_year = 2020
start_year = 1965
region = 'united_states'
project = 'haleu'

# paths to data and templates
import_data.merge_coordinates('../database/Year-end Reactor Status_' + str(data_year) + '.csv',
                              '../database/coordinates.sqlite', data_year)

pris_file = '../database/reactors_pris_' + str(data_year) + '.csv'
recipes = import_data.import_csv('../database/vision_recipes/uox.csv', ',')

deployinst_tmpl = '../templates/deployinst_template.xml'
inclusions_tmpl = '../templates/inclusions_template.xml'
recipe_template = import_data.load_template(
    '../templates/recipes_template.xml')
reactor_template = '../templates/reactors_template.xml'
cyclus_tmpl = ('../templates/' + region + '_template.xml')

recipe_path = '../input/' + project + '/inputs/' + region + '/recipes/'
deployment_path = '../input/' + project + '/inputs/' + region + '/buildtimes'
reactor_path = '../input/' + project + '/inputs/' + region + '/reactors'


pris = pd.read_csv(pris_file)


burnups = [33, 51, 100]
for bu in burnups:
    fresh = import_data.get_composition_fresh(recipes, bu)
    spent = import_data.get_composition_spent(recipes, bu)
    import_data.write_recipes(fresh, spent, recipe_template, bu, recipe_path)

reactor_list = import_data.select_region(pris, region, start_year)
import_data.write_reactors(
    reactor_list,
    reactor_path,
    reactor_template, start_year,
    18,
    1)  # change cycle and refuel time
buildtime = import_data.deploy_reactors(pris_file, region, start_year, deployinst_tmpl,
                                        inclusions_tmpl, reactor_path, deployment_path)

import_data.render_cyclus(
    cyclus_tmpl,
    region,
    buildtime,
    '../input/' +
    project +
    '/inputs/',
    start_year, 1500, 51)  # change burn up
