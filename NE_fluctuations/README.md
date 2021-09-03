# Nuclear envelope fluctuations analysis

This folder contains the example images to run the scripts for NE fluctuations analysis.

NB: the starting image here is cut from a larger field of view (single nucleus) and has already undergone bleach correction (output of NE_fluctuations_Part01).

* output of **NE_fluctuations_Part01**: image in *bleach_corr* folder

* output of **NE_fluctuations_Part02**: image in  *reg* folder (registered single nucleus)

* *kymo* folder: 4 kymographs associated with the nucleus and ROI list to go back to which region of the NE was used

* output of **NE_fluctuations_Part03**:

  * *single_kymo_analysis* folder (containing csv files with NE position, etc, for each kymograph)

  * *single_kymo_plots* folder (containing plots of single kymograph trajectories)

  * *MSD_analysis.csv* file (square root of the MSD for each kymograph)

* output of **NE_fluctuations_Part04**:

  * *single_cell_plot* folder (containing plots of the trajectories of all kymographs associated with each cell)
  * *MSD_analysis_percell.csv* file (average MSD square root per cell)
