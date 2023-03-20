import numpy as np
import sys
import os
from random import uniform
sys.path.append('../../../../../scripts')
import dakota_input as inp

counter = 0
for c_rate in [0.3, 0.584, 0.8]:
    for pop_size in [10, 25, 50]:
        for m_rate in [0.08, 0.1, 0.116, 0.15]:
            variable_dict = {'pop_size':pop_size,
                            'mutation_rate':m_rate,
                            'crossover_rate':c_rate,
                            'counter':counter}
            dakota_file = f"tuning_{counter}.in"
            inp.render_input("moga_tuning_template.in", variable_dict, dakota_file)

            counter += 1
