import numpy as np
import sys
import os
from random import uniform
sys.path.append('../../../../scripts')
import dakota_input as inp

f = open("tuning_results.csv", 'w')

counter = 0
for m_type in ['replace_uniform', 'offset_normal']:
    for pop_size in [5, 10, 25, 50, 100]:
        for c_penalty in range(4):         
            variable_dict = {'pop_size':pop_size,
                            'mutation_type':m_type,
                            'mutation_rate':np.round(uniform(0.01, 0.2),3),
                            'crossover_rate':np.round(uniform(0.1, 0.9),3),
                            'constraint':np.round(uniform(0.5, 2),3),
                            'counter':counter}
            dakota_file = f"tuning_{counter}.in"
            inp.render_input("min_haleu_template.in", variable_dict, dakota_file)

            f.write(m_type + "," + str(pop_size) + "," + str(c_penalty) + "," +
                    str(variable_dict['mutation_rate']) + "," + 
                    str(variable_dict['crossover_rate']) + "," +
                    str(variable_dict['constraint']) + ", \n") 
            counter += 1
