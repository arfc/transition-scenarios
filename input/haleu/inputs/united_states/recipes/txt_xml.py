from xml.dom import minidom 
import os 
import numpy as np

def write_recipe():
    root = minidom.Document()
    recipe = root.createElement('recipe')
    root.appendChild(recipe)

    data = np.genfromtxt("6pass.txt", dtype=str,skip_header=2)

    for item in data:
        nuclide = root.createElement('nuclide')
        nuclide_id = root.createElement('id')
        nuclide_comp = root.createElement('comp')

        id_txt = nuclide_id.Text(item[0])
        #nuclide_comp.setAttribute('comp', item[1])

        nuclide.appendChild(nuclide_id)
        nuclide.appendChild(nuclide_comp)
        recipe.appendChild(nuclide)

    xml_str = root.toprettyxml(newl='\n')

    with open("6pass.xml", "w") as f:
        f.write(xml_str)

def sample():
    dom = minidom.parse("6pass.xml")
    x = dom.createElement("foo")  # creates <foo />
    txt = dom.createTextNode("hello, world!")  # creates "hello, world!"
    x.appendChild(txt)  # results in <foo>hello, world!</foo>
    dom.childNodes[1].appendChild(x)  # appends at end of 1st child's children
    print(dom.toxml())

if __name__ == '__main__':
    write_recipe()
