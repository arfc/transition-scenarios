import pyne.material
import pyne.nucname
import matplotlib.pyplot as plt

c = {}
with open('./uox_used_fuel_recipe', 'r') as f:
    lines = f.readlines()
    for line in lines:
        if 'nuclide' in line:
             iso = line.split('id')[2]
             iso = iso.replace('>', '')
             iso = iso.replace('</', '')
             comp = line.split('comp')[1]
             comp = comp.replace('>', '')
             comp = comp.replace('</', '')
             c[iso] = float(comp)
print(c)
mat = pyne.material.from_atom_frac(c)
print(mat)
z=0
np = 0
pu = 0
am = 0
cm = 0
sumz = sum(mat.values())
mat = mat.decay(3600*24*365*6)
for key, val in mat.items():
    valz = val / sumz
    if 'Pu' in pyne.nucname.name(key):
        z += valz
    if 'Np' in pyne.nucname.name(key):
        z += valz
    if 'Am' in pyne.nucname.name(key):
        z += valz
    if 'Cm' in pyne.nucname.name(key):
        z += valz
print(z)

dictz = {}
for key, val in mat.items():
    valz = val / sumz
    iso = pyne.nucname.name(key)
    if 'Pu' in pyne.nucname.name(key):
        dictz[iso] = valz / z
    if 'Np' in pyne.nucname.name(key):
        dictz[iso] = valz / z
    if 'Am' in pyne.nucname.name(key):
        dictz[iso] = valz / z
    if 'Cm' in pyne.nucname.name(key):
        dictz[iso] = valz / z


for key, val in dictz.items():
    print('%s : %f' %(key, val)) 


lit = {'Np237': 0.048,
       'Pu238': 0.0213,
       'Pu239': 0.4833,
       'Pu240': 0.2217,
       'Pu241': 0.0905,
       'Pu242': 0.0638,
       'Am241': 0.0517,
       'Am243': 0.0148,
       'Cm244': 0.0043}

lit_val = []
valz = []
nums = []
labels = []
z = 1
for key, val in lit.items():
    try:
        lit_val.append(lit[key])
    except:
        lit_val.append(0)
    valz.append(dictz[key])
    nums.append(z)
    labels.append(key)
    z += 1 

fig, ax1 = plt.subplots()
color1 = 'r'
color2 = 'b'

err = [(x-y) / x for x,y in zip(lit_val, valz)]

ax1.scatter(labels, lit_val, label='REBUS-3700 TRU comp')
ax1.scatter(labels, valz, label='51 GWdth/MTHM Recipe')
plt.xticks(size='small')
plt.legend()
plt.show()

#ax2 = ax1.twinx()
#ax2.scatter(labels, err, color='r')
#plt.show()