## Builds the US reactor fleet as a Bright-lite input from the fleet text file. 

template = open('Bright-lite_temp', 'r').readlines()
fleet = open('US Fleet.txt', 'r').readlines()
institution = open('institution', 'r').readlines()
input_text = open('USFleet.temp', 'r').readlines()
input_file = open('USFleet.xml', 'w')

for li in input_text:	
	if "ADDFACS" in li:
		for line in fleet:
			line = line.split('\t')
			temp_reactor = list(template)
			for lineT in temp_reactor:
				if "TEMP_NAME" in lineT:
					lineT = lineT.replace("TEMP_NAME", line[0])
				if "TEMP_LIFE" in lineT:
					lineT = lineT.replace("TEMP_LIFE", line[6])
				if "TEMP_POWER" in lineT:
					lineT = lineT.replace("TEMP_POWER", line[1])
				if "TEMP_MASS" in lineT:
					lineT = lineT.replace("TEMP_MASS", line[8])
				if "TEMP_TYPE" in lineT:
					lineT = lineT.replace("TEMP_TYPE", line[4])
				if "</burnup_time>" in lineT:
					i = 0
					while i < 11:
						value = (int(line[28+(4*i)])-1958)*12
						temp_string1 = "           <item><key>" +str(value)+ "</key>"
						temp_string2 = "<val>" +str(line[25+(4*i)]) + "</val></item>\n"
						input_file.write(temp_string1+temp_string2)
						i+=1
				if "</avail_time>" in lineT:
					i = 0
					while i < 11:
						value = (int(line[28+(4*i)])-1958)*12
						temp_string1 = "           <item><key>" +str(value)+ "</key>"
						temp_string2 = "<val>" +str(line[27+(4*i)]) + "</val></item>\n"
						input_file.write(temp_string1+temp_string2)
						i+=1
				input_file.write(lineT)
		continue
	if "ADDINST" in li:
		for line in institution:
			if "</prototypes>" in line:
				for reactor in fleet:
					reactor = reactor.split('\t')
					input_file.write("<val>" + reactor[0] + "</val>")
			if "</build_times>" in line:
				for reactor in fleet:
					reactor = reactor.split('\t')
					input_file.write("<val>" + reactor[5] + "</val>")
			if "</n_build>" in line:
				for reactor in fleet:
					reactor = reactor.split('\t')
					input_file.write("<val>1</val>")
			input_file.write(line)
		continue
	input_file.write(li)
input_file.close()			


