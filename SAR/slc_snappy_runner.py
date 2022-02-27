import subprocess

pipeline_out = subprocess.call(['python', 'SAR/SLC_processing.py', '-j', 'SAR/slc_settings.json'])