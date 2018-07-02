import subprocess
import os

folders = [x[0] for x in os.walk('.')]
folders = [x for x in folders if 'growth' in x]

with open('log.txt') as f: 
    for directory in folders:
        print('RUNNING %s:' %directory[2:])
        if os.path.isfile('%s/output.sqlite' %directory):
            f.write('%s IS ALREADY THERE' %directory)
            continue
        bash_command = 'cyclus %s/compiled_input.xml -o %s/output.sqlite --warn-limit 0' %(directory, directory)
        lint_command = 'xmllint --xinclude -o %s/compiled_input.xml %s/input.xml' %(directory,directory)
        lint = subprocess.Popen(lint_command.split(), stdout=subprocess.PIPE)
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        f.write('FINISHED %s' %directory)
        output, error = process.communicate()
        print(output)
        print(error)