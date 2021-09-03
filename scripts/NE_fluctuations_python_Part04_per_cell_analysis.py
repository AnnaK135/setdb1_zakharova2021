#!/usr/bin/python3.8

###
# Aim: calculate NE fluctuation per cell based on single kymograph analysis by NE_fluctuations_Part01_single_kymo_analysis.py
# from Nishit Srivastava, adapted by Alice Williart
# The code was developed for GNU/Linux OS and will require alteration if run on another OS, in particular switching from pathlib.PurePosixPath to pathlib.PureWindowsPath.
# input:
# 	- acquisitions.csv file containing following columns:
# 		- experiment index
# 		- absolute path to the folder containing the 'kymo' folder (plugin used requires GNU/Linux OS)
# 		- experiment name (will figure in summary results file)
# 		(- timelapse (s))
# 		(- pixel size (um))
# 		(- initial timepoint: timepoint at which analysis should start)
# 		(- final timepoint: timepoint at which analysis should end (typically if the cell starts dying towards the end of acquisition))
# 	- folders:
#		- 'kymo' containing the kymographs, name finishing with kymo.tif, and the ROIs used for reslice in zip file named <kymo_name>_kymo_ROI.zip
#		- 'analysis' containing the <experiment_name>_MSD_analysis.csv file as obtained by NE_fluctuations_Part01_single_kymo_analysis.py
# output:
#	- folders: (folders will be created if they don't already exist)
# 		- subfolder in 'analysis': 'single_cell_plots' to save one graph per cell with all the trajectories used for each cell
#	- <experiment_name>_MSD_analysis_percell.csv containing the average sqr MSD and standard deviation for all the cells.
###

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import pathlib

counter = 0
acquisition = pd.read_csv('acquisitions.csv')

# folder: 'single_kymo_analysis'
exp_index = int(input('Experiment index: '))
main_dir = acquisition['path'][exp_index]

main_analysis_dir = pathlib.PurePosixPath(f'{main_dir}/analysis')

# mkdir in folder 'analysis'
input_dir = pathlib.PurePosixPath(f'{main_analysis_dir}/single_kymo_analysis')

if os.path.isdir(f'{main_analysis_dir}/single_cell_plots')==False:
	os.mkdir(f'{main_analysis_dir}/single_cell_plots')

output_dir_cells = pathlib.PurePosixPath(f'{main_analysis_dir}/single_cell_plots')

# list all kymo analyses
list_kymo = [f for f in os.listdir(input_dir) if f.endswith('analysis.csv')]
list_kymo = pd.Series(list_kymo)

# list all single cells
list_all = os.listdir(f'{main_dir}/kymo')
list_ROI = [f for f in list_all if f.endswith('.zip')]
ext = len('_kymo_ROI.zip')
list_cells = []

for i in range(len(list_ROI)):
	list_cells.append(list_ROI[i][0:-ext])

# import summary results table
results = [f for f in os.listdir(main_analysis_dir) if f.endswith('analysis.csv')]
results = results[0]
results_file = pd.read_csv(f'{main_analysis_dir}/{results}')

MSD_percell = pd.DataFrame()

for i in range(len(list_cells)):
	name, ext = os.path.splitext(list_cells[i])
	list_cells[i] = name

print(list_cells)

# loop on all single cell names:
## identify kymo analyses csv files belonging to same cell and plot trajectories
## calculate MSD per cell

for cell_index in range(len(list_cells)):
	counter+=1

	# plot trajectories
	is_cell = np.array([])

	## retrieve kymos from the cell i

	for kymo_index in range(len(list_kymo)):
		ext2 = len('_kymo_01_kymo_analysis.csv')
		if list_kymo[kymo_index][0:-ext2]==list_cells[cell_index]:
			is_cell = np.concatenate([is_cell, [True]])
		else:
			is_cell = np.concatenate([is_cell, [False]])

	is_cell = is_cell.astype(bool)

	## if cell i has kymos: plot all four kymos trajectories on the same figure

	if np.sum(is_cell)>0:
		cell_files = list_kymo[is_cell]

		fig = plt.figure()
		sbplot = fig.add_subplot(1, 1, 1)

		colors = ['lightgreen', 'forestgreen', 'springgreen', 'mediumaquamarine', 'paleturquoise', 'teal', 'darkturquoise', 'deepskyblue', 'skyblue', 'cornflowerblue', 'royalblue', 'mediumblue', 'slateblue', 'darkviolet', 'plum', 'purple', 'mediumvioletred', 'lightcoral', 'darkred', 'red', 'tomato', 'orangered', 'sienna', 'darkorange', 'tan', 'goldenrod']
		index = 0
		legend_lines = []
		legend_text = []

		for kymo in cell_files:
			index+=1
			table = pd.read_csv(f'{input_dir}/{kymo}') # import single kymo results table
			deviation = table['deviation (nm)']
			sbplot.plot(deviation, '-', color=colors[index], linewidth=0.5)
			sbplot.set_xlabel('time')
			sbplot.set_ylabel('displacement (nm)')
			sbplot.set_title(f'{list_cells[cell_index]}')

			kymo_name, ext = os.path.splitext(kymo)

			# center axes

			ax = plt.gca()
			ax.spines['left'].set_position(('data', 0.0))
			ax.spines['bottom'].set_position(('data', 0.0))
			ax.spines['right'].set_color('none')
			ax.spines['top'].set_color('none')

			ext3 = len('_kymo_analysis')
			pre = len('kymo_01_kymo_analysis')

			legend_text = legend_text + [kymo_name[len(kymo_name)-pre:len(kymo_name)-ext3]]
			legend_lines = legend_lines + [Line2D([0], [0], color=colors[index], linewidth=0.5)]

		sbplot.legend(legend_lines, legend_text)

		plt.savefig(f'{output_dir_cells}/{list_cells[cell_index]}_plot.png', dpi=300)
		plt.close(fig=fig)

	# calculate sqr MSD/cell

	## retrieve the results for the kymos from cell i

	is_cell_table = results_file['file']

	is_cell_results = np.array([])

	ext4 = len('_kymo_01')

	for result_index in range(is_cell_table.shape[0]):

		if is_cell_table[result_index][0:-ext4]==list_cells[cell_index]:
			is_cell_results = np.concatenate([is_cell_results, [True]])
		elif is_cell_table[result_index][0:-ext4]==list_cells[cell_index]:
			is_cell_results = np.concatenate([is_cell_results, [True]])
		else:
			is_cell_results = np.concatenate([is_cell_results, [False]])

	is_cell_results = is_cell_results.astype(bool)

	if np.sum(is_cell_results)>0:

		## extract condition of cell i as well as MSDs of kymos from cell i

		cell_subtable = results_file[is_cell_results]
		cell_MSDs = cell_subtable['sqr MSD (nm)']
		cell_thresholded_MSDs = cell_subtable['sqr MSD (thresholded) (nm)']
		condition = list_cells[cell_index][0:3]

		## calculate mean sqr MSD on all kymos for cell i and standard dev
		mean_MSD = np.average(cell_MSDs)
		mean_thresholded_MSD = np.average(cell_thresholded_MSDs)
		stdev_MSD = np.std(cell_MSDs)
		stdev_thresholded_MSD = np.std(cell_thresholded_MSDs)

		## setup dataframe with condition, mean MSD on all kymos for cell i and standard dev

		d = {'condition': condition, 'cell': list_cells[cell_index], 'mean sqr MSD (nm)': [mean_MSD], 'std deviation (nm)': [stdev_MSD], 'mean sqr MSD (thresholded) (nm)' : [mean_thresholded_MSD], 'std deviation (thresholded) (nm)' : [stdev_thresholded_MSD]}

		MSD_percell = MSD_percell.append(pd.DataFrame(d))

	print(f'{counter} cell(s) processed out of {len(list_cells)}')

#MSD_percell = MSD_percell.sort_values(by=['condition'])
MSD_percell.to_csv(f'{main_analysis_dir}/{results[0:-4]}_percell.csv')
print('Done!')