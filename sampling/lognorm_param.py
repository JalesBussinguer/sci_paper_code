from scipy.stats import lognorm
import pandas as pd
import os

files_path = 'D:/thesis_data/VEG_INDICES/samples/stratified/savanica/100m/'

output_path = 'D:/thesis_data/VEG_INDICES/lognorm_params/savanica/100m/'

files_list = os.listdir(files_path)

for index, file in enumerate(files_list):

    date = files_list[index].split('_')[1]

    if os.path.exists(output_path + 'FS_' + date + '_ln_params.csv'):
        print('file already exists!')
        continue

    samples_file = pd.read_csv(files_path + file)

    dprvi_patches = samples_file.filter(regex='^dprvi_patch', axis=1)
    rvi_patches = samples_file.filter(regex='^rvi_patch', axis=1)
    prvi_patches = samples_file.filter(regex='^prvi_patch', axis=1)
    dpsvi_patches = samples_file.filter(regex='^dpsvi_patch', axis=1)
    dpsvim_patches = samples_file.filter(regex='^dpsvim_patch', axis=1)
    
    index_dict = {'dprvi': dprvi_patches, 'rvi': rvi_patches, 'prvi': prvi_patches, 'dpsvi': dpsvi_patches, 'dpsvim': dpsvim_patches}

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

    result.to_csv(output_path + 'FS_' + date + '_ln_params.csv', sep=',', index=False)
    print(f'{date} csv file saved!')