 /*
* ImgageJ macro
* This macro calculates paxillin-positive area and nuclei number
* to be futher used for calculating normalized paxillin area
*
*To customize settings:
* enter the paths to the image folders in your system;
* after the first run adjust the setThreshold parameters in the functions countNUC and paxArea so that they best fit your images.
*/
 
 while (nImages>0) { 
          selectImage(nImages); 
          close(); 
      } 

/*
* enter the paths to the folders with DAPI and GFP stained images below
*/
inputGFP = "path_to_the_folder_with_GFP_stained_images";
inputDAPI = "path_to_the_folder_with_DAPI_stained_images"; 
listGFP = getFileList(inputGFP);
listDAPI = getFileList(inputDAPI);

function countNUC(inputDAPI, filename) {
	open(inputDAPI + filename);
	title = getTitle();
	run("Subtract Background...", "rolling=200");
	run("Split Channels");
	selectImage(title + " (red)");
	close();
	selectImage(title + " (blue)");
	setAutoThreshold("Default dark");
	//run("Threshold...");
	//setThreshold(57, 255);
	setOption("BlackBackground", true);
	run("Convert to Mask");
	run("Erode");
	run("Erode");
	run("Erode");
	run("Watershed");
	run("Analyze Particles...", "size=5000-Infinity show=[Overlay Masks] clear summarize");
}

function paxArea(inputGFP, filename) {
	open(inputGFP + filename);
	title = getTitle();
	run("Subtract Background...", "rolling=50");
	run("Split Channels");
	selectImage(title + " (red)");
	close();
	selectImage(title + " (green)");
	run("Despeckle");
	setAutoThreshold("Default dark");
	//run("Threshold...");
	//setThreshold(37, 255);
	setOption("BlackBackground", true);
	run("Convert to Mask");
	run("Select All");
	run("Measure");
}

for (i = 0; i < listDAPI.length; i++){
	countNUC(inputDAPI, listDAPI[i]);
}

for (i = 0; i < listGFP.length; i++){
	print(listGFP[i]);
	paxArea(inputGFP, listGFP[i]);
}

