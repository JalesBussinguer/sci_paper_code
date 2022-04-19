from scipy.stats import kruskal as kw_test
import pandas as pd
import os

florestal_path = 'D:/thesis_data/VEG_INDICES/samples/florestal/'
savanica_path = 'D:/thesis_data/VEG_INDICES/samples/savanica/'
campestre_path = 'D:/thesis_data/VEG_INDICES/samples/campestre/'

florestal_files_list = os.listdir(florestal_path)
savanica_files_list = os.listdir(savanica_path)
campestre_files_list = os.listdir(campestre_path)

dataframe = pd.DataFrame(columns=['statistic','p_value','H0_status'])

for id, file in enumerate(florestal_files_list):

    # H0: The population median of all groups are equal

    date_ff = pd.read_csv(florestal_path + florestal_files_list[id])
    date_fs = pd.read_csv(savanica_path + savanica_files_list[id])
    date_fc = pd.read_csv(campestre_path + campestre_files_list[id])

    statistic, p_value = kw_test(date_ff['RVI'], date_fs['RVI'], date_fc['RVI'])

    if p_value < 0.05:
        h0_status = 'reject'
    else:
        h0_status = 'accept'

    data_dict = {'statistic': [statistic], 'p_value': [p_value], 'H0_status': [h0_status]}
    
    data_concat = pd.DataFrame(data_dict)

    dataframe = pd.concat([data_concat, dataframe])

    print(f'test {id} done!')

dataframe.to_csv('D:/thesis_data/VEG_INDICES/stats/kruskal_tests/RVI_kruskal_test.csv', sep=',', index=False)
print(f'Kruskal test csv file saved!')