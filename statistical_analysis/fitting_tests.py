from fitter import Fitter
import pandas as pd
import os

florestal_path = 'D:/thesis_data/VEG_INDICES/samples/ff_dists/'
savanica_path = 'D:/thesis_data/VEG_INDICES/samples/fs_dists/'
campestre_path = 'D:/thesis_data/VEG_INDICES/samples/fc_dists/'

florestal_files_list = os.listdir(florestal_path)
savanica_files_list = os.listdir(savanica_path)
campestre_files_list = os.listdir(campestre_path)

dataframe = pd.DataFrame()

for id, file in enumerate(florestal_files_list):

    # H0: The population median of all groups are equal

    date_ff = pd.read_csv(florestal_path + florestal_files_list[id])
    date_fs = pd.read_csv(savanica_path + savanica_files_list[id])
    date_fc = pd.read_csv(campestre_path + campestre_files_list[id])

    f = Fitter(date_fc['DPSVI'], distributions=['norm', 'lognorm'])
    fit = f.fit()
    test = f.summary()

    teste = pd.DataFrame(f.get_best().values())
    teste['dist'] = f.get_best().keys()
    teste['sumsquare_error'] = test['sumsquare_error'][0]

    cols = teste.columns.tolist()
    cols = cols[-2:] + cols[:-2]
    df = teste[cols]

    dataframe = pd.concat([df, dataframe])

    print(f'test {id} done!')

dataframe.to_csv('D:/thesis_data/VEG_INDICES/stats/fit_tests/FF_DpRVI_fit_test.csv', sep=',', index=False)
print(f'Fit test csv file saved!')