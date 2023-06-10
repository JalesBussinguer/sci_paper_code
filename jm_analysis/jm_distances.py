import numpy as np
import pandas as pd
import os

def jm_distances_normal(set_1, set_2):

    set_1_mean = np.mean(set_1)
    set_2_mean = np.mean(set_2)
    
    set_1_std = np.std(set_1)
    set_2_std = np.std(set_2)

    sigma_1 = np.power(set_1_std, 2)
    sigma_2 = np.power(set_2_std, 2)

    # The Bhattacharyya distance between two normal distributions
    b_dist = 0.25 * np.log(0.25 * (sigma_1/sigma_2) + (sigma_1/sigma_2) + 2) + 0.25 * ((set_1_mean-set_2_mean)**2 / sigma_1 + sigma_2)

    # Jeffries-Matusita distance
    jm_dist = np.sqrt(2 * (1 - np.exp(-b_dist)))
    
    return jm_dist

class1_path = 'D:/thesis_data/VEG_INDICES/samples/fs_dists/'
class2_path = 'D:/thesis_data/VEG_INDICES/samples/fc_dists/'

class1_list= os.listdir(class1_path)
class2_list= os.listdir(class2_path)
    
index_list = ['DpRVI', 'PRVI','DPSVI', 'DPSVIm', 'RVI']

data = {}

for i in range(len(os.listdir(class1_path))):

    class1_df = pd.read_csv(class1_path + os.listdir(class1_path)[i])
    class2_df = pd.read_csv(class2_path + os.listdir(class2_path)[i])

    for index in index_list:
        
        class1 = class1_df.filter(regex=f'^{index}', axis=1).values
        class2 = class2_df.filter(regex=f'^{index}', axis=1).values

        if index not in data:
            data[index] = []

        jm_dist = jm_distances_normal(class1, class2)

        data[index].append(jm_dist)
    
    print(f'test {i} done!')

result = pd.DataFrame(data)
    
output_path = 'D:/thesis_data/VEG_INDICES/jm_dists/'

result.to_csv(output_path + 'FS_FC_jm_dists.csv', sep=',', index=False)


