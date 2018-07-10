import subprocess
import os

folders = [x[0] for x in os.walk('.')]
folders = [x for x in folders if 'growth' in x]
restart = True
with open('log.txt', 'w') as f: 
    for directory in folders:
        print('RUNNING %s:' %directory[2:])
        if os.path.isfile('%s/compiled_input.xml' %directory):
            os.remove('%s/compiled_input.xml' %directory)
        