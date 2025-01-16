import pandas as pd
import os
import glob

def calculate_statistics(folder_path, start_index=852):
    # Get all CSV files in the folder
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

    # Calculate statistics
    statistics = {}

    # Read each CSV file and append to the DataFrame
    for file in csv_files:
        df = pd.read_csv(file)
        print('the file is',file)

        for column in df.columns:
            df[column] = pd.to_numeric(df[column], errors='coerce')

            selection_series = df[column][start_index:] # values after the transition year

            statistics[f'{file}_{column}'] = {
                'average': df[column][start_index:].mean(),
                'max': df[column][start_index:].max(),
                'min': selection_series[selection_series>0].min(),
                'stand': df[column][start_index:].std()
                }
    return statistics



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

    metrics = ['fresh', 'used', 'swu', 'reactors']

    rows = ['ng', '5', '15', '1', '2']
    for metric in metrics:
        average_results_df = pd.DataFrame(index=rows)
        max_results_df = pd.DataFrame(index=rows)
        min_results_df = pd.DataFrame(index=rows)
        stan_dev_results_df = pd.DataFrame(index=rows)

        for fuel in databases.keys():
            for direc in databases[fuel].keys():
                dfold = f'{fuel}/{direc}/{metric}/'
                start_index = 852
                values_df = calculate_statistics(base_folder + dfold, start_index)

                for key, value in values_df.items():
                    ref = key.split(base_folder + dfold)[-1]
                    name = ref.split('_')[-1]
                    if 'ng' in ref:
                        average_results_df.loc['ng', f'{name}_{metric}'] = value['average']
                        max_results_df.loc['ng', f'{name}_{metric}'] = value['max']
                        min_results_df.loc['ng', f'{name}_{metric}'] = value['min']
                        stan_dev_results_df.loc['ng', f'{name}_{metric}'] = value['stand']

                    elif '15' in ref:
                        average_results_df.loc['15', f'{name}_{metric}'] = value['average']
                        max_results_df.loc['15', f'{name}_{metric}'] = value['max']
                        min_results_df.loc['15', f'{name}_{metric}'] = value['min']
                        stan_dev_results_df.loc['15', f'{name}_{metric}'] = value['stand']

                    elif '5' in ref:
                        average_results_df.loc['5', f'{name}_{metric}'] = value['average']
                        max_results_df.loc['5', f'{name}_{metric}'] = value['max']
                        min_results_df.loc['5', f'{name}_{metric}'] = value['min']
                        stan_dev_results_df.loc['5', f'{name}_{metric}'] = value['stand']


                    elif '2' in ref:
                        average_results_df.loc['2', f'{name}_{metric}'] = value['average']
                        max_results_df.loc['2', f'{name}_{metric}'] = value['max']
                        min_results_df.loc['2', f'{name}_{metric}'] = value['min']
                        stan_dev_results_df.loc['2', f'{name}_{metric}'] = value['stand']


                    elif '1' in ref:
                        average_results_df.loc['1', f'{name}_{metric}'] = value['average']
                        max_results_df.loc['1', f'{name}_{metric}'] = value['max']
                        min_results_df.loc['1', f'{name}_{metric}'] = value['min']
                        stan_dev_results_df.loc['1', f'{name}_{metric}'] = value['stand']


                # save the results to a csv
                average_results_df.to_csv(base_folder + f'{metric}/{fuel}_{direc}_{metric}_avg_calcs' + '.csv')
                max_results_df.to_csv(base_folder + f'{metric}/{fuel}_{direc}_{metric}_max_calcs' + '.csv')
                min_results_df.to_csv(base_folder + f'{metric}/{fuel}_{direc}_{metric}_min_calcs' + '.csv')
                stan_dev_results_df.to_csv(base_folder + f'{metric}/{fuel}_{direc}_{metric}_stan_dev_calcs' + '.csv')