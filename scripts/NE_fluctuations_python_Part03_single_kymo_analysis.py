#!/usr/bin/python3.8

###
# Aim: calculate NE fluctuation in x based on kymographs obtained after pre-processing and analysis in Fiji of the movies (see Fiji macros parts 1 and 2)
# from Nishit Srivastava, adapted by Alice Williart
# data architecture: all kymos in one folder, at the same level as the 'analysis' folder
# 'analysis' folder will contain a 'single_kymo_plots' folder for plots, a 'single_kymo_analysis' folder for csv
# summary .csv is saved in 'analysis' folder
# input:
# 	- acquisitions.csv file containing following columns:
# 		- 'experiment index': integer, each has to be unique
# 		- 'path': absolute path to the folder containing the 'kymo' folder (plugin used requires GNU/Linux OS)
# 		- 'experiment name' (will figure in summary results file)
# 		- 'timelapse (s)'
# 		- 'pixel size (um)'
# 		- 'initial timepoint': timepoint at which analysis should start
# 		- 'final timepoint': timepoint at which analysis should end (typically if the cell starts dying towards the end of acquisition)
# 	- folder 'kymo' containing the kymographs, name finishing with kymo.tif
# output:
#	- folders: (folders will be created if they don't already exist)
# 		- subfolder in 'analysis': 'single_kymo_plots'
# 			- one graph per kymo (NE trajectory)
# 		- subfolder in 'analysis': 'single_kymo_analysis'
# 			- one .csv file per kymo containing NE position at each timepoint and distance to average NE position
#	- <experiment_name>_MSD_analysis.csv containing the average sqr MSD with or without threshold in pixel and nm for all the kymos.
###

import numpy as np
import matplotlib.pyplot as plt
from skimage import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import pathlib

acquisition = pd.read_csv('acquisitions.csv')
exp_index = int(input('Experiment index: '))
main_dir = acquisition['path'][exp_index]
kymo_dir = pathlib.PurePosixPath(f'{main_dir}/kymo')

# make analysis subfolders if they don't already exist

if os.path.isdir(f'{kymo_dir.parent}/analysis')==False:
	os.mkdir(f'{kymo_dir.parent}/analysis')
main_analysis_dir = pathlib.PurePosixPath(f'{kymo_dir.parent}/analysis')

if os.path.isdir(f'{kymo_dir.parent}/analysis/single_kymo_plots')==False:
	os.mkdir(f'{kymo_dir.parent}/analysis/single_kymo_plots')
kymo_plots_dir = pathlib.PurePosixPath(f'{kymo_dir.parent}/analysis/single_kymo_plots')

if os.path.isdir(f'{kymo_dir.parent}/analysis/single_kymo_analysis')==False:
	os.mkdir(f'{kymo_dir.parent}/analysis/single_kymo_analysis')
kymo_csv_dir = pathlib.PurePosixPath(f'{kymo_dir.parent}/analysis/single_kymo_analysis')

dir_list = os.listdir(kymo_dir)
filename = [f for f in os.listdir(kymo_dir) if f.endswith('.tif')]

experiment = acquisition['experiment'][exp_index]
nb_kymo = len(filename)
nb_processed = 0

timelapse = acquisition['timelapse (s)'][exp_index]

crop_min = int(acquisition['initial timepoint'][exp_index])
crop_max = int(acquisition['final timepoint'][exp_index])

pixel_size = acquisition['pixel size (um)'][exp_index]

MSD_d = pd.DataFrame()

low_quality = pd.DataFrame()

for img in filename:

	nb_processed+=1

	kymo_name = img
	print (kymo_name[0:-8])

	kymo = io.imread(f'{kymo_dir}/{img}')
	y_length = min(crop_max, kymo.shape[0])


	# crop kymograph to remove the first few lines and cuts at <crop_max> final timepoint - arbitrary - to prevent points that drifted / when cells start to die

	kymo_crop = kymo[crop_min:y_length,:]

	index_max= np.argmax(kymo_crop, axis =1)

	name,ext =os.path.splitext(img)

	kymo_d = pd.DataFrame()

	max_parabola = np.array([])
	threshold_nm = np.array([])

	for i in range(len(index_max)):

		# for each row (=timepoint), determine 8-pixel range around the detected maximum

		values_range = kymo_crop[i,index_max[i]-3:index_max[i]+4]
		index_range = (index_max[i]-3,index_max[i]-2,index_max[i]-1,index_max[i],index_max[i]+1,index_max[i]+2,index_max[i]+3)

		# quality check: doesn't take the kymo into account if at certain timepoints, the maximum is too close to the edge to do the fit

		if len(index_range)==len(values_range):
			quality = True
		else: # if quality is not good enough, kymo name is added to the 'bad file' list with first timepoint at which there was a problem
			quality =  False
			bad_file = {'name' : name, 'bad timepoint' : i}
			low_quality = low_quality.append(bad_file, ignore_index=True)
			print(f'{name} doesn\'t have enough good timepoints')
			break

		# fit a parabola in the range around maximum to place NE

		if quality==True:

			a = np.polyfit(index_range,values_range,2) # output: tuple (a, b, c) for y=ax2+bx+c

			max_parabola_i = np.array([-(a[1]/(2*a[0]))])
			max_parabola = np.concatenate([max_parabola, max_parabola_i])

			df = {'timepoint' : crop_min+i, 'time (s)' : i*timelapse, 'index range around maximum' : [index_range], 'values range around maximum' : [values_range], 'max parabola' : max_parabola_i}
			df = pd.DataFrame(df)
			kymo_d = kymo_d.append(df)

	if quality==True:

		# calculate mean NE position
		x_mean = np.mean(max_parabola)

		# calculate deviation from mean at each timepoint
		deviation_pix = max_parabola-x_mean
		deviation_nm = deviation_pix*pixel_size*1000
		kymo_d['deviation (pixel)'] = deviation_pix
		kymo_d['deviation (nm)'] = deviation_nm

		# filter out timepoints with deviation from mean >2x average deviation for 'thresholded' values
		threshold = 2*np.average(np.abs(deviation_nm))
		thresholded = np.abs(deviation_nm)<threshold
		below_thresh = np.sum(thresholded)

		for i in range(len(index_max)):
			threshold_nm = np.concatenate([threshold_nm, np.array([threshold])])

		kymo_d['threshold (nm)'] = threshold_nm
		kymo_d['thresholded deviation'] = thresholded

		# calculate square root of mean square displacement (MSD) for the kymograph kymo
		MSD_pix = np.sqrt(np.sum(deviation_pix**2)/(crop_max-crop_min))
		MSD_pix_thresh = np.sqrt(np.sum(deviation_pix[thresholded]**2)/below_thresh)
		MSD_nm = np.sqrt(np.sum(deviation_nm**2)/(crop_max-crop_min))
		MSD_nm_thresh = np.sqrt(np.sum(deviation_nm[thresholded]**2)/below_thresh)

		kymo_d.to_csv(f'{kymo_csv_dir}/{name}_kymo_analysis.csv')

		MSD_img = {'condition' : [name[0:3]], 'file' : [name], 'mean NE position' : [x_mean], 'sqr MSD (pixel)' : [MSD_pix], 'sqr MSD (nm)' : [MSD_nm], 'threshold' : [threshold], 'sqr MSD (thresholded) (pixel)' : [MSD_pix_thresh], 'sqr MSD (thresholded) (nm)' : [MSD_nm_thresh]}
		MSD_img = pd.DataFrame(MSD_img)

		MSD_d = MSD_d.append(MSD_img)

		time = kymo_d['time (s)']

		# plot individual trajectory

		fig = plt.figure()
		sbplot = fig.add_subplot(1, 1, 1)
		sbplot.set_title(f'{name}')
		sbplot.plot(time, deviation_nm, '-')
		sbplot.plot(time, threshold_nm, ':b')
		sbplot.plot(time, -threshold_nm, ':b')
		sbplot.set_xlabel('time (s)')
		sbplot.set_ylabel('displacement (nm)')

		ax = plt.gca()

		## spine placement data centered
		ax.spines['left'].set_position(('data', 0.0))
		ax.spines['bottom'].set_position(('data', 0.0))
		ax.spines['right'].set_color('none')
		ax.spines['top'].set_color('none')

		plt.savefig(f'{kymo_plots_dir}/{name}_plot.png', dpi=300)
		plt.close(fig=fig)

	print(f'{nb_processed} kymo(s) processed out of {nb_kymo}')

MSD_d = MSD_d.sort_values(by=['condition'])
MSD_d.to_csv(f'{main_analysis_dir}/{experiment}_t{crop_min}-{crop_max}_MSD_analysis.csv')
low_quality.to_csv(f'{main_analysis_dir}/bad_files.txt')
print('Done!')