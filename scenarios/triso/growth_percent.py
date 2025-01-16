import os
import pandas as pd

def calculate_growth_rate(df, start_index=72):
    growth_rates = []
    column = df.columns.to_list()[1]
    for i in range(start_index, len(df) - 1):
        initial_value = df[column].iloc[i]
        final_value = df[column].iloc[i + 1]
        growth_rate = (final_value - initial_value) / initial_value
        growth_rates.append(growth_rate)
    average_growth_rate = sum(growth_rates) / len(growth_rates)

    max_growth_rate = max(growth_rates)
    min_growth_rate = min(growth_rates)
    mode_growth_rate = max(set(growth_rates), key=growth_rates.count)

    growth_variables = [average_growth_rate, max_growth_rate, min_growth_rate, mode_growth_rate]

    return growth_variables

def process_csv_files(base_folder, start_index):
    growth_rates_dict = {}
    rows = ['average', 'max', 'min', 'mode']

    growth_rates_df = pd.DataFrame(index=rows)

    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                truncated_path = os.path.splitext(os.path.join(*file_path.split(os.sep)[-1:]))[0]
                df = pd.read_csv(file_path)
                growth_rates = calculate_growth_rate(df, start_index)
                growth_rates_df[truncated_path] = growth_rates

    return growth_rates_df

databases = {
    'one_fuel':{
        'rand_greed_one': ['drg1', 'drg2', 'drg5', 'drg15', 'drgng'],
        'random': ['dr1', 'dr2', 'dr5', 'dr15', 'drng'],
        'greedy': ['dg1', 'dg2', 'dg5', 'dg15', 'dgng']
        },
    'multi_fuel':{
        'greedy': ['dg1', 'dg2', 'dg5', 'dg15', 'dgng'],
        'rand_greed': ['drg1', 'drg2', 'drg5', 'drg15', 'drgng'],
        'random': ['dr1', 'dr2', 'dr5', 'dr15', 'drng']
        },
}

if __name__ == "__main__":
    base_folder = '../../../../../../../media/nsryan/Elements/scenes/analysis/'

    metric = 'energy'

    rows = ['ng', '5', '15', '1', '2']
    average_results_df = pd.DataFrame(index=rows)
    max_results_df = pd.DataFrame(index=rows)
    min_results_df = pd.DataFrame(index=rows)
    mode_results_df = pd.DataFrame(index=rows)

    for fuel in databases.keys():
        for direc in databases[fuel].keys():
            average_results_df[fuel+'_'+direc] = 0
            max_results_df[fuel+'_'+direc] = 0
            min_results_df[fuel+'_'+direc] = 0
            mode_results_df[fuel+'_'+direc] = 0

    for fuel in databases.keys():
        for direc in databases[fuel].keys():
            dfold = f'{fuel}/{direc}/{metric}/'
            start_index = 72
            growth_rates_df = process_csv_files(base_folder + dfold, start_index)

            for col in range(len(growth_rates_df.columns)):
                column = growth_rates_df.columns[col]
                if 'ng' in column:
                    average_results_df.loc['ng', fuel+'_'+direc] = growth_rates_df[column][0]
                    max_results_df.loc['ng', fuel+'_'+direc] = growth_rates_df[column][1]
                    min_results_df.loc['ng', fuel+'_'+direc] = growth_rates_df[column][2]
                    mode_results_df.loc['ng', fuel+'_'+direc] = growth_rates_df[column][3]
                if '15' in column:
                    average_results_df.loc['15', fuel+'_'+direc] = growth_rates_df[column][0]
                    max_results_df.loc['15', fuel+'_'+direc] = growth_rates_df[column][1]
                    min_results_df.loc['15', fuel+'_'+direc] = growth_rates_df[column][2]
                    mode_results_df.loc['15', fuel+'_'+direc] = growth_rates_df[column][3]
                if '5' in column:
                    average_results_df.loc['5', fuel+'_'+direc] = growth_rates_df[column][0]
                    max_results_df.loc['5', fuel+'_'+direc] = growth_rates_df[column][1]
                    min_results_df.loc['5', fuel+'_'+direc] = growth_rates_df[column][2]
                    mode_results_df.loc['5', fuel+'_'+direc] = growth_rates_df[column][3]
                if '2' in column:
                    average_results_df.loc['2', fuel+'_'+direc] = growth_rates_df[column][0]
                    max_results_df.loc['2', fuel+'_'+direc] = growth_rates_df[column][1]
                    min_results_df.loc['2', fuel+'_'+direc] = growth_rates_df[column][2]
                    mode_results_df.loc['2', fuel+'_'+direc] = growth_rates_df[column][3]
                if '1' in column:
                    average_results_df.loc['1', fuel+'_'+direc] = growth_rates_df[column][0]
                    max_results_df.loc['1', fuel+'_'+direc] = growth_rates_df[column][1]
                    min_results_df.loc['1', fuel+'_'+direc] = growth_rates_df[column][2]
                    mode_results_df.loc['1', fuel+'_'+direc] = growth_rates_df[column][3]


    # save the results to a csv
    average_results_df.to_csv(base_folder + f'{metric}_avg_growth_rates' + '.csv')
    max_results_df.to_csv(base_folder + f'{metric}_max_growth_rates' + '.csv')
    min_results_df.to_csv(base_folder + f'{metric}_min_growth_rates' + '.csv')
    mode_results_df.to_csv(base_folder + f'{metric}_mode_growth_rates' + '.csv')