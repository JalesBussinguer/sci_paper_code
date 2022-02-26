import subprocess

pipeline_out = subprocess.call(['python', 'SAR/GRD_preprocessing.py', '-j', 'SAR/grd_settings.json'])