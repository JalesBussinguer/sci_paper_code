import pandas as pd
import os
import numpy as np

def overlap_coefficient(arr1, arr2, number_bins):
    # Determine the range over which the integration will occur
    min_value = min(np.min(arr1), np.min(arr2))
    max_value = max(np.max(arr1), np.max(arr2))
    
    # Calculate the histogram for each array
    hist_arr1, _ = np.histogram(arr1, bins=number_bins, range=(min_value, max_value))
    hist_arr2, _ = np.histogram(arr2, bins=number_bins, range=(min_value, max_value))

    normed_hist1 = hist_arr1 / len(arr1)
    normed_hist2 = hist_arr2 / len(arr2)
    
    # Calculate the overlap coefficient
    min_arr = np.minimum(normed_hist1, normed_hist2)
    overlap_coeff = np.sum(min_arr)
    
    return overlap_coeff

class1_path = 'D:/thesis_data/VEG_INDICES/samples/fs_dists/'
class2_path = 'D:/thesis_data/VEG_INDICES/samples/fc_dists/'

data = {}

index_list = ['DpRVI', 'PRVI','DPSVI', 'DPSVIm', 'RVI']

output_path = 'D:/thesis_data/VEG_INDICES/ovl/'

for id, _ in enumerate(os.listdir(class1_path)):

    class1_df = pd.read_csv(class1_path + os.listdir(class1_path)[id])
    class2_df = pd.read_csv(class2_path + os.listdir(class2_path)[id])

    for index in index_list:

        class1_data = [value[0] for value in class1_df.filter(regex=f'^{index}', axis=1).values]
        class2_data = [value[0] for value in class2_df.filter(regex=f'^{index}', axis=1).values]

        if index not in data:
            data[index] = []

        results = overlap_coefficient(class1_data, class2_data, 500)
        
        data[index].append(results)

    print(id)
    
out_df = pd.DataFrame(data)

out_df.to_csv(output_path+'FS_FC_OVL_500_bins.csv', sep=',', index=False)
