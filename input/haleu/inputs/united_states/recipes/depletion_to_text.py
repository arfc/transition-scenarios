from pyne import data
from pyne.material import Material
from pyne import serpent
from pyne import nucname

dep = serpent.parse_dep(
    '../../../../../../uiuc-microreactors/usnc/memo-fullcore9_dep.m')

mats = dep['MAT_un_MATERIAL']
# mats[1].comp.keys (commented out)
newdict = {k: v for k, v in mats[10].comp.items()}

comp_string = ""
for k, v in newdict.items():
    comp_string = comp_string + '{}'.format(k) + " " + str(v) + "\n"


with open("mmr_comps.txt", "w") as f:
    f.write(comp_string)
