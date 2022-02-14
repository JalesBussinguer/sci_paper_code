import subprocess

pipeline_out = subprocess.call(['python', 'SAR/SLC_processing.py', '-j', 'slc_settings.json'])