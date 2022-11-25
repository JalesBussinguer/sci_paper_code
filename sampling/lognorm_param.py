from scipy.stats import lognorm
import pandas as pd
import os

files_path = 'D:/thesis_data/VEG_INDICES/dpsvi_parameters/samples/GL/'

output_path = 'D:/thesis_data/VEG_INDICES/dpsvi_parameters/lognorm_params/GL/'

files_list = os.listdir(files_path)

for index, file in enumerate(files_list):

    samples_file = pd.read_csv(files_path + file)

    #dprvi_patches = samples_file.filter(regex='^dprvi_patch', axis=1)
    #prvi_patches = samples_file.filter(regex='^prvi_patch', axis=1)
    dpsvi_patches = samples_file.filter(regex='^dpsvi_patch', axis=1)
    #dpsvim_patches = samples_file.filter(regex='^dpsvim_patch', axis=1)
    #rvi_patches = samples_file.filter(regex='^rvi_patch', axis=1)

    index_dict = {'dpsvi': dpsvi_patches}

    date = files_list[index].split('_')[1]

    data = {}

    for index, df in index_dict.items():

        for column in df.columns:

            samples = df[column]

            shape,_,scale = lognorm.fit(samples)

            shape_col = f'{index}_shape'
            scale_col = f'{index}_scale'

            if shape_col not in data:
                data[shape_col] = []

            if scale_col not in data:
                data[scale_col] = []

            data[shape_col].append(shape)
            data[scale_col].append(scale)

    result = pd.DataFrame(data)

    result.to_csv(output_path + 'GL_' + date + '_ln_params.csv', sep=',', index=False)
    print(f'{date} csv file saved!')