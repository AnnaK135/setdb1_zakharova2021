// NE fluctuations: segmentation of the nuclei and registration overtime to correct for translation and rotation movements
// input: bleach-corrected movies from NE_fluctuations_pre-processing_bleach_corection.ijm
// output: registraetd single-nucleus movies, on which line kymographs will be made

input_path = getDirectory("Input directory: ");
output_path_single_cells = getDirectory("Output directory for single cells: ");
output_path_reg = getDirectory("Output directory for registrated cells: ");

setBatchMode(true);

if(isOpen("Results")==true) {
	selectWindow("Results");
	run("Close");
}
roiManager("reset");
run("Close All");

list = getFileList(input_path);

for (i = 0; i < lengthOf(list); i++) {

	print(list[i]);
	roiManager("reset");
	open(input_path+list[i]);
	name = File.nameWithoutExtension;
	rename(name);
	Stack.getDimensions(width, height, channels, slices, frames);

	// segmentation by thresholding on the NE channel (EGFP-LAP2b)
	run("Duplicate...", "title=nucleus_mask duplicate");
	run("Z Project...", "projection=[Max Intensity]");
	run("Median...", "radius=2");
	setAutoThreshold("Huang dark");
	run("Convert to Mask");

	run("Analyze Particles...", "size=1000-Infinity circularity=0.00-1.00 include add");

	selectWindow("nucleus_mask");
	close();
	nb_nuclei = roiManager("count");

	if (nb_nuclei > 0) {
		roiManager("save", output_path_single_cells+name+"_nucleiROI.zip");

		for (k = 0; k < nb_nuclei; k++) {
			index = k+1;
			// make single nucleus image based on detected particles in segmentation (with enlarging step to allow for thresholding errors)
			selectWindow(name);
			roiManager("select", k);
			run("Enlarge...", "enlarge=4");
			run("Duplicate...", "title="+name+"_"+index+" duplicate");
			saveAs("tif", output_path_single_cells+name+"_"+index+".tif");

			for (j=0; j < slices; j++) {
				setOption("ScaleConversions", true);
			}

			// registration using StackReg plugin, Rigid Body correcting for translation and rotation
			run("StackReg", "transformation=[Rigid Body]");
			saveAs("tif", output_path_reg+name+"_"+index+"_reg.tif");

			selectWindow(name+"_"+index+"_reg.tif");
			close();
		}
	}
	selectWindow(name);
	close();
	run("Close All");
}
run("Close All");