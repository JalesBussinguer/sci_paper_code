import os

from scipy.stats import chi2
from math import log
import pandas as pd
import numpy as np


class1_path = 'D:/thesis_data/VEG_INDICES/lognorm_params/savanica/'
class2_path = 'D:/thesis_data/VEG_INDICES/lognorm_params/campestre/'

data = {}

index_list = ['dprvi', 'prvi','dpsvi', 'dpsvim', 'rvi']

for id, _ in enumerate(os.listdir(class1_path)):

    class1_df = pd.read_csv(class1_path + os.listdir(class1_path)[id])
    class2_df = pd.read_csv(class2_path + os.listdir(class2_path)[id])
    
    for index in index_list:
        
        class1_shape = class1_df.filter(regex=f'^{index}_shape', axis=1).values
        class1_scale = class1_df.filter(regex=f'^{index}_scale', axis=1).values

        class2_shape = class2_df.filter(regex=f'^{index}_shape', axis=1).values
        class2_scale = class2_df.filter(regex=f'^{index}_scale', axis=1).values

        matrix = np.zeros([len(class1_shape), len(class2_shape)])

        if index not in data:
            data[index] = []

        for i in class1_df.index:
            for j in class2_df.index:

                mu_p = log(class1_scale[i])
                mu_q = log(class2_scale[j])

                var_p = np.power(class1_shape[i], 2)
                var_q = np.power(class2_shape[j], 2)

                m = 400
                n = 400

                # Kullback-Leibler distances (simmetrized)
                dskl_ln = (var_p * np.power((mu_p - mu_q), 2) + var_q * np.power((mu_q - mu_p), 2) + np.power((var_p - var_q), 2)) / (4 * var_p * var_q)

                s = ((2*m*n) / (m + n)) * dskl_ln # statistic

                p_value = chi2.sf(s, df=2)

                if p_value <= 0.05:
                    matrix[i, j] = 1
                    
                if p_value > 0.05:
                    matrix[i, j] = 0
        
        m = matrix.shape[0]
        idx = (np.arange(1, m+1) + (m+1) * np.arange(m - 1)[:, None]).reshape(m, -1)
        out = matrix.ravel()[idx]

        rate = (out.sum() / (out.shape[0] * out.shape[1]))
    
        data[index].append(rate)

    print(id)
        
result = pd.DataFrame(data)

output_path = 'D:/thesis_data/VEG_INDICES/rates/'

result.to_csv(output_path + 'FS_FC_rates.csv', sep=',', index=False)