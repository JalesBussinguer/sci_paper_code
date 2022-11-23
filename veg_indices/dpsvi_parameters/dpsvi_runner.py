import subprocess

pipeline_out = subprocess.call(['python', 'veg_indices/dpsvi_parameters/dpsvi_parameters.py', '-j', 'veg_indices/dpsvi_parameters/settings.json'])