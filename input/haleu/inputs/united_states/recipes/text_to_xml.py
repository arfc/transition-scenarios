from xml.dom import minidom 
import os 
import numpy as np

def write_recipe():
    root = minidom.Document()
    recipe = root.createElement('recipe')
    root.appendChild(recipe)

    data = np.genfromtxt("mmr_comps.txt", dtype=str,skip_header=2)

    for item in data:
        nuclide = root.createElement('nuclide')
        nuclide_id = root.createElement('id')
        nuclide_comp = root.createElement('comp')

        id_txt = root.createTextNode(item[0])
        comp = item[1]
        comp_txt = root.createTextNode(comp)

        nuclide_id.appendChild(id_txt)
        nuclide_comp.appendChild(comp_txt)
        nuclide.appendChild(nuclide_id)
        nuclide.appendChild(nuclide_comp)
        recipe.appendChild(nuclide)

    xml_str = root.toprettyxml(newl='\n')

    with open("mmr_comps.xml", "w") as f:
        f.write(xml_str)

if __name__ == '__main__':
    write_recipe()
