import sys

sys.path.append('../../../../../scripts')
import dakota_input as inp

counter = 0
for c_rate in [0.3, 0.584, 0.8]:
    variable_dict = {'pop_size':50,
                     'mutation_rate':0.08,
                     'crossover_rate':c_rate,
                     'counter':counter}
    dakota_file = f"tuning_{counter}.in"
    inp.render_input("moga_tuning_template.in", variable_dict, dakota_file)

    counter += 1
for pop_size in [100, 25, 50]:
    variable_dict = {'pop_size':pop_size,
                     'mutation_rate':0.08,
                     'crossover_rate':0.8,
                     'counter':counter}
    dakota_file = f"tuning_{counter}.in"
    inp.render_input("moga_tuning_template.in", variable_dict, dakota_file)
    counter += 1

for m_rate in [0.08, 0.1, 0.116, 0.15]:
    variable_dict = {'pop_size':25,
                     'mutation_rate':m_rate,
                     'crossover_rate':0.8,
                     'counter':counter}
    dakota_file = f"tuning_{counter}.in"
    inp.render_input("moga_tuning_template.in", variable_dict, dakota_file)

    counter += 1
