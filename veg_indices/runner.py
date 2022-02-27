import subprocess

pipeline_out = subprocess.call(['python', 'veg_indices/SAR_vegetation_indices.py', '-j', 'veg_indices/settings.json'])