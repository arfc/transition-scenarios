import subprocess
import os
from shutil import copyfile

folders = [x[0] for x in os.walk('.')]
folders = [x for x in folders if 'growth' in x]
restart = True
for directory in folders:
    print('RUNNING %s:' %directory[2:])
    try:
        os.remove('%s/recipe.sqlite' %directory)
    except:
        print('STARTING NEW')
    # copy blanket file
    print('RUNNING RECIPE')
    bash_command = 'cyclus %s/compiled_recipe.xml -o %s/recipe.sqlite --warn-limit 0' %(directory, directory)
    lint_command = 'xmllint --xinclude -o %s/compiled_recipe.xml %s/udb_recipe.xml' %(directory,directory)
    lint = subprocess.Popen(lint_command.split(), stdout=subprocess.PIPE)
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(error)