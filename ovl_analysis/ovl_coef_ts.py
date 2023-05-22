import pandas as pd
import os
import numpy as np

def OVL_two_random_arr(arr1, arr2, number_bins):
    # Determine the range over which the integration will occur
    min_value = np.min((min(arr1), min(arr2)))
    max_value = np.min((max(arr1), max(arr2)))
    # Determine the bin width
    bin_width = (max_value-min_value)/number_bins
    #For each bin, find min frequency
    lower_bound = min_value #Lower bound of the first bin is the min_value of both arrays
    min_arr = np.empty(number_bins) #Array that will collect the min frequency in each bin
    for b in range(number_bins):
        higher_bound = lower_bound + bin_width #Set the higher bound for the bin
        #Determine the share of samples in the interval
        freq_arr1 = np.ma.masked_where((arr1<lower_bound)|(arr1>=higher_bound), arr1).count()/len(arr1)
        freq_arr2 = np.ma.masked_where((arr2<lower_bound)|(arr2>=higher_bound), arr2).count()/len(arr2)
        #Conserve the lower frequency
        min_arr[b] = np.min((freq_arr1, freq_arr2))
        lower_bound = higher_bound #To move to the next range
    return min_arr.sum()  

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

        results = OVL_two_random_arr(class1_data, class2_data, 10)
        
        data[index].append(results)

    print(id)
    
out_df = pd.DataFrame(data)

out_df.to_csv(output_path+'FS_FC_OVL_10bins.csv', sep=',', index=False)


# def overlap_coef(x,y):

#     _mux = np.mean(x)
#     _sigmax = np.std(x)

#     _muy = np.mean(y)
#     _sigmay = np.std(y)

#     if (_sigmax, _mux) < (_sigmay, _muy):   # sort to assure commutativity
#         x, y = y, x

#     X_var, Y_var = x.variance, y.variance

#     dv = Y_var - X_var
#     dm = fabs(_muy - _mux)

#     if not dv:
#         return 1.0 - erf(dm / (2.0 * _sigmax * sqrt(2.0)))
    
#     a = _mux * Y_var - _muy * X_var
#     b = _sigmax * _sigmay * sqrt(dm**2.0 + dv * log(Y_var / X_var))
#     x1 = (a + b) / dv
#     x2 = (a - b) / dv

#     return 1.0 - (fabs(y.cdf(x1) - x.cdf(x1)) + fabs(y.cdf(x2) - x.cdf(x2)))
