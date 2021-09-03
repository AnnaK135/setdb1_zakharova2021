#!/usr/bin/python3.8

###
# Aim: build a summary results table for the PIV analysis by retrieving the values for each nucleus, as obtained by the Fiji macros 'chromatin mobility' Parts 1 and 2.
# The input files have to be organised as follows: directory called 'analysis_PIV', containing one subfolder / nucleus, named <img_name>_<nuc_nb>_PIV, containing the PIV files.
# input:
# 	-acquisitions.csv file containing the following columns:
# 		- 'experiment'
# 		- 'path' (containing the path to the parent folder of the 'analysis' folder, which contains the results of rotation measurements))
#		- 'PIV_frame_nb' (number of images analysed for the PIV, i.e. number of .txt files in each subfolder)
# output: .csv file containing for each nucleus the average PIV magnitude value
###

import pandas as pd
import numpy as np
import os
import pathlib

exp_index = int(input('Experiment index: '))
acquisition = pd.read_csv('acquisitions.csv')

main_dir = pathlib.PurePosixPath(acquisition['path'][exp_index])
main_analysis_dir = pathlib.PurePosixPath(f'{main_dir}/analysis')

if os.path.isdir(f'{main_dir}/analysis_PIV')==False:
	os.mkdir(f'{main_dir}/analysis_PIV')
PIV_dir = pathlib.PurePosixPath(f'{main_dir}/analysis_PIV')
PIV_dir_list = os.listdir(PIV_dir)

if os.path.isdir(f'{main_dir}/summary_analysis')==False:
	os.mkdir(f'{main_dir}/summary_analysis')
summary_analysis_dir = pathlib.PurePosixPath(f'{main_dir}/summary_analysis')

exp = acquisition['experiment'][exp_index]

print('starting PIV analysis...')

nb_PIV_frames = acquisition['PIV_frame_nb'][exp_index]
column_magnitude_PIV = 4 # 5th column of the PIV results table but indexing starts at 0

# PIV_subdir is the list of the subfolders in analysis_PIV
PIV_subdir = []

for d in PIV_dir_list:
	if d[-3]!='.' and d[-4]!='.': #excludes from listing files having an extension of two or three characters (most often .py or .csv/zip/tif/png)
		PIV_subdir.append(d)

PIV_results = pd.DataFrame()

for d in PIV_subdir:
	print(f'analysing {d}')

	PIV_subdir_list = os.listdir(f'{PIV_dir}/{d}')

	files = [f for f in PIV_subdir_list if f.endswith('.txt')]

	PIV_magn = np.zeros(nb_PIV_frames)

	counter = 0

	for f in files:
		table = pd.read_csv(f'{PIV_dir}/{d}/{f}', sep=' ', header=None)

		PIV_magnitude_column = np.array(table[column_magnitude_PIV]) # retrieve the column containing the PIV magnitude

		corrected_PIV_magn_col = PIV_magnitude_column[PIV_magnitude_column != 0] # exclude points at which PIV is equal to 0, i.e. background outside of the nucleus

		PIV_magn[counter] = np.average(corrected_PIV_magn_col)
		counter+=1

	print(np.average(PIV_magn))
	d = {'nucleus' : f'{d[0:-4]}', 'PIV_magnitude' : [np.average(PIV_magn)]}
	df = pd.DataFrame(d)

	PIV_results = PIV_results.append(df)

PIV_results.to_csv(f'{summary_analysis_dir}/{exp}_results_PIV_scaled-rotation.csv')

print('PIV analysis done')