import pandas as pd

import cymetric as cm
import transition_metrics as tm

outfile = '../outputs/xe100_1percent.sqlite'

transactions = tm.add_receiver_prototype(outfile)
transactions.to_csv('xe_1percent_transactions.csv')
