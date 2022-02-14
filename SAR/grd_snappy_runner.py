import subprocess

pipeline_out = subprocess.call(['python', 'SAR/GRD_processing.py', '-j', 'grd_settings.json'])