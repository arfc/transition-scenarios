import os
import numpy as np
import pandas as pd

directory = '../lwrs/'

# Check if the directory exists
if os.path.exists(directory):
    file_list = os.listdir(directory)
    stripped_file_list = [os.path.splitext(file)[0] for file in file_list if file.endswith('.xml')]
    print(stripped_file_list)
else:
    print(f"Directory '{directory}' does not exist.")

# make a random start date after 2030 before 2105
# start_random_dates = np.random.randint((2030-1959)*12, (2105-1959)*12, size=len(stripped_file_list)).tolist()

# pull the start year for each reactor from the "Startup date (year) b" column in ../lwr_info.csv
start_dates = []
reacs = []
with open('lwr_info.csv', 'r') as f:
    for line in f:
        start_dates.append(line.split(',')[6])
        reacs.append(line.split(',')[1])

dates = ['1974', '1978', '1976', '1987', '1964', '1987', '1988', '1973', '1974', '1976', '1976', '1974', '1985', '1987', '1984', '1974', '1976', '1985', '1986', '1987', '1984', '1990', '1993', '1974', '1977', '1974', '1976', '1977', '1984', '1985', '1959', '1969', '1971', '1974', '1985', '1977', '1981', '1974', '1973', '1969', '1984', '1967', '1986', '1974', '1978', '1986', '1962', '1962', '1973', '1975', '1973', '1967', '1982', '1983', '1985', '1989', '1973', '1981', '1983', '1970', '1975', '1986', '1970', '1969', '1987', '1978', '1980', '1973', '1973', '1974', '1969', '1971', '1985', '1986', '1987', '1973', '1974', '1986', '1972', '1970', '1971', '1973', '1974', '1972', '1972', '1974', '1985', '1970', '1976', '1981', '1967', '1982', '1982', '1990', '1980', '1981', '1986', '1988', '1989', '1976', '1983', '1982', '1972', '1973', '1982', '1984', '1974', '1978', '1975', '1972', '1973', '1972', '1987', '1989', '2023', '2024', '1985', '1996', '2016', '1985', '1960', '1973', '1973']

for date in range(len(dates)):
    dates[date] = (int(dates[date]) - 1958) * 12

# # make a pandas dataframe from the start date and the reactor name
# df = pd.DataFrame({'start_date': dates, 'reactor': reacs[1:]})

# df_sorted = df.sort_values(by='start_date')

print(dates)
print(len(dates))
# print(df)
# print(df_sorted)
# print(df_sorted['reactor'].tolist())
# print(df_sorted['start_date'].tolist())
# print(len(df_sorted['reactor'].tolist()))
# print(len(df_sorted['start_date'].tolist()))

# check which reactors are in stripped_file_list, but not in reacs
for reactor in stripped_file_list:
    if reactor not in reacs:
        print(reactor)