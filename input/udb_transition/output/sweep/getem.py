import subprocess
import os
from shutil import copyfile

folders = [x[0] for x in os.walk('../../')]
folders = [x for x in folders if 'growth' in x]
folders = [x.replace('../../', '') for x in folders]
print(folders)
for directory in folders:
    command1 = "sshpass -e scp teddy@128.174.163.139:~/github/us_trans/input/udb_transition/%s/no.sqlite %s_no.sqlite" %(directory, directory)
    command2 = "sshpass -e scp teddy@128.174.163.139:~/github/us_trans/input/udb_transition/%s/precise.sqlite %s_precise.sqlite" %(directory, directory)
    command3 = "sshpass -e scp teddy@128.174.163.139:~/github/us_trans/input/udb_transition/%s/recipe.sqlite %s_recipe.sqlite" %(directory, directory)
    process1 = subprocess.Popen(command1.split(), stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    process1.stdout.readlines()
    process2 = subprocess.Popen(command2.split(), stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    process2.stdout.readlines()
    output, error = process2.communicate()
    process3 = subprocess.Popen(command3.split(), stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    process3.stdout.readlines()
    output, error = process3.communicate()

