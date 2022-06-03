import os

from scipy.stats import chi2
from math import log
import pandas as pd
import numpy as np


file_path = 'D:/thesis_data/VEG_INDICES/lognorm_params/campestre/'

data = {}

index_list = ['dprvi', 'prvi','dpsvi', 'dpsvim', 'rvi']

for file in os.listdir(file_path):
    
    df = pd.read_csv(file_path + file)

    for index in index_list:
        
        shape = df.filter(regex=f'^{index}_shape', axis=1).values
        scale = df.filter(regex=f'^{index}_scale', axis=1).values

        matrix = np.zeros([len(shape), len(scale)])

        if index not in data:
            data[index] = []

        for i in df.index:
            for j in df.index:

                scale_p = scale[i]
                scale_q = scale[j]

                shape_p = np.power(shape[i], 2)
                shape_q = np.power(shape[j], 2)

                mu_p = log(scale[i])
                mu_q = log(scale[j])

                var_p = np.power(shape[i], 2)
                var_q = np.power(shape[j], 2)

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

        rate = (out.sum() / (out.shape[0]*out.shape[1]))
    
        data[index].append(rate)

    print(file)
        
result = pd.DataFrame(data)

output_path = 'D:/thesis_data/VEG_INDICES/rates/'

result.to_csv(output_path + 'FC_rates.csv', sep=',', index=False)