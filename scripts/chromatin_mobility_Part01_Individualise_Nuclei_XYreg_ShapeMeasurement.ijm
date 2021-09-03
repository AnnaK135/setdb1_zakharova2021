/// Chromatin mobility by PIV - developed by Mathieu Maurin, adapted by Alice Williart///

/*
Aim: detect, track and register nuclei overtime
Thresholding-based segmentation, tracking using 3D object counter plugin
Registration correcting for XY translation and rotation using MultiStackReg plugin based on nucleus mask

Input: one Z-plane movie with only one channel (nuclear staining)
Output:
	- objects map movie (output of 3D OC) showing nucleus tracking results and movie of nucleus masks
	- for each nucleus:
		- .csv file containing successive XY coordinates of its center of mass overtime
		- transformation matrix of the registration step
		- registered mask movie
		- registered movie
*/


dir = getDirectory("Input directory");
dir_list = getFileList(dir);
dirOut = getDirectory("Output directory");

run("Close All");

setBatchMode(true);

for (img = 0; img < lengthOf(dir_list); img++) {
	if (endsWith(dir_list[img], ".tif")) {

		open(dir+dir_list[img]);
		run("Select None");

		name=getTitle();
		shortName=substring(name,0, lengthOf(name)-4);

		run("Set Measurements...", "area mean centroid shape stack redirect=None decimal=3");

		if(isOpen("Results")==true) {
			selectWindow("Results");
			run("Close");
		}

		// make nuclei mask
		selectWindow(name);
		run("Duplicate...", "title=mask duplicate");
		run("Mean...", "radius=3 stack");
		run("Auto Threshold", "method=Default white stack");

		// 3D object counter to track the nuclei
		Stack.getDimensions(w,h,chan,slic,fram);
		getVoxelSize(Rx, Ry, Rz, unit);
		run("Properties...", "channels="+chan+" slices="+fram+" frames="+slic+" unit="+unit+" pixel_width="+Rx+" pixel_height="+Ry+" voxel_depth="+Rz);

		//add black image on the top and the bottom of the stack for the exclude on edge option
		setSlice(1);
		run("Select All");
		run("Copy");
		run("Clear", "slice");
		run("Add Slice", "add=slice");
		setSlice(2);
		run("Paste");
		setSlice(fram+1);
		run("Add Slice", "add=slice");

		run("3D Objects Counter", "threshold=128 slice=1 min.=1000 max.=4732800 exclude_objects_on_edges objects statistics");

		IJ.renameResults("Results");
		nbTrackedNuclei=nResults();

		if(isOpen("Results")==true) {
			selectWindow("Results");
			run("Close");
		}

		selectWindow("Objects map of mask");
		setSlice(1);
		run("Delete Slice", "delete=slice");
		setSlice(fram);
		run("Delete Slice", "delete=slice");

		selectWindow("mask");
		setSlice(1);
		run("Delete Slice", "delete=slice");
		setSlice(fram+1);
		run("Delete Slice", "delete=slice");

		print(shortName);

		// measure shapes and individualise nucleis
		for(nucl=1;nucl<=nbTrackedNuclei;nucl++) {
			selectWindow("Objects map of mask");
			run("Duplicate...", "title=nucl_"+nucl+" duplicate");
			setThreshold(nucl,nucl);
			run("Convert to Mask", "method=Default background=Huang black");
			run("Analyze Particles...", "size=500-Infinity pixel display exclude clear stack");
			selectWindow("Results");
			saveAs("Results",dirOut+shortName+"_nucl_"+nucl+".csv");

			// crop around each nucleus (max Z on all timepoints to make sure they do not get out of the field of view) - faster for registration
			selectWindow("nucl_"+nucl);
			run("Fill Holes", "stack");
			run("Duplicate...", "title=temp duplicate");
			run("Z Project...", "projection=[Max Intensity]");
			//run("Invert");
			run("Create Selection");
			run("Enlarge...", "enlarge=4.88");
			getSelectionBounds(x, y, width, height);
			selectWindow("MAX_temp");
			run("Close");
			selectWindow("temp");
			run("Close");
			selectWindow("nucl_"+nucl);
			makeRectangle(x, y, width + 10, height + 10);
			run("Crop");
			run("Duplicate...", "title=temp duplicate");
			saveAs("Tiff",dirOut+shortName+"_nucl_"+nucl+"_mask.tif");
			run("Close");

			// registration: scaled rotation for translation and rotation correction

			selectWindow("nucl_"+nucl);
			run("MultiStackReg", "stack_1=nucl_"+nucl+" action_1=Align file_1=["+dirOut+shortName+"_transformationMatrix_scaled_rotation_nucl_"+nucl+"] stack_2=None action_2=Ignore file_2=[] transformation=[Scaled Rotation] save");
			saveAs("Tiff",dirOut+shortName+"_nucl_"+nucl+"_mask_reg_scaled-rotation.tif");
			run("Close");

			selectWindow(name);
			makeRectangle(x, y, width, height);
			run("Duplicate...", "title=tmp duplicate");
			selectWindow("tmp");
			run("MultiStackReg", "stack_1=tmp action_1=[Load Transformation File] file_1=["+dirOut+shortName+"_transformationMatrix_scaled_rotation_nucl_"+nucl+"] stack_2=None action_2=Ignore file_2=[] transformation=[Scaled Rotation]");
			saveAs("Tiff",dirOut+shortName+"_nucl_"+nucl+"_reg_scaled-rotation.tif");
			run("Close");
		}

		// save mask and object map
		selectWindow("Objects map of mask");
		saveAs("Tiff",dirOut+shortName+"_ObjectMap.tif");

		selectWindow("mask");
		saveAs("Tiff",dirOut+shortName+"_Mask.tif");

		run("Close All");
	}
}