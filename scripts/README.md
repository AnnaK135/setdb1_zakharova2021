# Scripts for image analysis

This folder contains the scripts for chromatin mobility analysis and nuclear envelope fluctuation anlaysis.

## Chromatin mobility

* **rawdata**: one-plane one-channel movies (nuclear staining)

* **chromatin_mobility_Part01** (ImageJ macro):
segmentation and registration (mathematical operation to correct for XY translation and rotation) of the nuclei

* **chromatin_mobility_Part02** (ImageJ macro): PIV analysis on individual registered nuclei.
For each pixel, the algorithm defines a block of a certain size centered on it and looks for similar patterns around it.

* **chromatin_mobility_Part03** (Python script): retrieve the values in the separate tables and calculate the average values of chromatin displacement.

## NE fluctuations

* **rawdata**: one-plane, one-channel movies (NE staining)

* **NE_fluctuations_Part01** (ImageJ macro):
bleach correction

* **NE_fluctuations_Part02** (ImageJ macro):
segmentation and registration of the nuclei

* **manual step**:
drawing of 4 lines/nucleus, at different positions in the NE and overtime reslice to follow how the NE is displaced

* **NE_fluctuations_Part03** (Python script):
kymograph analysis

  * determination of NE position at each timepoint

  * distance to average NE position

  * calculation of mean square displacement (MSD) square root taking into account all the timepoints (no threshold) or excluding outlier timepoints for which the displacement is twice as large as the average displacement (thresholded)

* **NE_fluctuations_Part04** (Python script):
regrouping all the kymograph belonging to the same cells and averaging of the values to obtain a MSD square root value (average displacement) per cell
