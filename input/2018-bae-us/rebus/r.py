file = './discharge'
with open(file+'_recipe.xml', 'w') as w:
    w.write('<root>\n')
    w.write('  <recipe>\n')
    w.write('    <name>%s</name>\n' %file.replace('./', ''))
    w.write('    <basis>mass</basis>\n')
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace('(', '')
            line = line.replace(',', '')
            line = line.replace("'", '')
            line = line.replace(')', '')
            line = line.strip().split()
            if float(line[0]) == 0.0:
                continue
            w.write('    <nuclide> <id>%s</id> <comp>%s</comp> </nuclide>\n' %(line[1], line[0]))
    w.write('  </recipe>\n')
    w.write('</root>')
