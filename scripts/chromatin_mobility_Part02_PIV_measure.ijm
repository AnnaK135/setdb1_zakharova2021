/// Chromatin mobility by PIV - developed by Mathieu Maurin, adapted by Alice Williart///

/*
Aim: perform PIV analysis on registered nuclei
PIV analysis in one iteration after averaging image t and t+1 and doubling the number of pixels to smooth the image

Input: folder containing the movies of nuclei registered for scaled rotation (output of part01) and their masks (<movie_nucleus_name>_reg_scaled-rotation.tif and <movie_nucleus_name>_mask_reg_scaled-rotation.tif)
Output: for each nucleus, one folder with:
	- image stacks with vectors and density of movement
	- image of flow between timepoint n and n+1
	- .csv file with the results of the PIV
	No header on the file, columns headers are as follow:
	x y ux1 uy1 mag1 ang1 p1 ux2 uy2 mag2 ang2 p2 ux0 uy0 mag0 flag
	x,y: pixel coordinates
	ux1, uy1: vector coordinates for PIV iteration 1
	mag1: vector norm for PIV iteration 1
	etc
*/

selectWindow("Log");
run("Close");

dir=getDirectory("Choose the folder with the registered nuclei:");
pathOut = getDirectory("Choose folder to save the analysis:");

fileList=getFileList(dir);

nbTimeforPIVanalysis=getNumber("Number of timepoints to analyse for the PIV:", 10);

print(nbTimeforPIVanalysis);
selectWindow("Log");
saveAs("txt", pathOut+"nbframes.txt");

//choose number of timepoints to perform the PIV analysis - ideally, try several.

run("Close All");

setBatchMode(true);

for(file=0;file<lengthOf(fileList);file++) {
	fileName=fileList[file];
	print(fileName);
	roiManager("Reset");
	if(endsWith(fileName,"_mask_reg_scaled-rotation.tif")==true) {
		shortName=substring(fileName,0,lengthOf(fileName)-lengthOf("_mask_reg_scaled-rotation.tif"));
		open(dir+fileName);
		open(dir+shortName+"_reg_scaled-rotation.tif");

		dirOut=pathOut+shortName+"_PIV"+File.separator();
		File.makeDirectory(dirOut);

		selectWindow(fileName);
		run("Z Project...", "stop="+nbTimeforPIVanalysis+" projection=[Max Intensity]");

		selectWindow("MAX_"+fileName);
		setOption("BlackBackground", true);
		run("Convert to Mask");
		run("Create Selection");

		getSelectionBounds(x,y,w,h);
		makeRectangle(x-20,y-20,w+40,h+40);
 		// select the nucleus with a thin band of background - reduce the number of pixels analysed by the PIV plugin for time-effectiveness
		roiManager("add");
		run("Select None");

		selectWindow("MAX_"+fileName);
		run("Close");

		// set background value (=outside the mask of the nucleus) to 0 to minimise noise detection (random movement in the background)
		// consequence: the PIV magnitude values (mag1) will be different from 0 only inside the nucleus (required for analysis in subsequent step)

		selectWindow(fileName);
		run("Divide...", "value=255.000 stack");
		imageCalculator("Multiply create stack", shortName+"_reg_scaled-rotation.tif",fileName);

		selectWindow("Result of "+shortName+"_reg_scaled-rotation.tif");
		roiManager("Select",0);
		run("Duplicate...", "title="+shortName+"_forPIV duplicate range=1-"+nbTimeforPIVanalysis);
		Stack.getDimensions(w,h,chan,slic,fram);

		//doubles the number of pixels of the image: smoother image to reduce the noise
		w1=2*w;
		h1=2*h;

		selectWindow(fileName);
		run("Close");
		selectWindow(shortName+"_reg_scaled-rotation.tif");
		run("Close");
		selectWindow("Result of "+shortName+"_reg_scaled-rotation.tif");
		run("Close");

		for(t=1;t<fram;t++) {
			t1=t+1;
			// average image of two consecutive timeframes
			selectWindow(shortName+"_forPIV");
			run("Duplicate...", "title="+t+"_"+t1+" duplicate range="+t+"-"+t1+"");
			run("Size...", "width="+w1+" height="+h1+" depth=2 constrain average interpolation=Bilinear");
			run("Mean...", "radius=2 stack");

			//one round of PIV (possibility for doing several), with parameters block size 16 and search window 32 (neighboourhood in which the plugin looks for pattern of the block to trace movement)

			run("iterative PIV(Basic)...", "piv1=16 sw1=32 piv2=0 sw2=0 piv3=0 sw3=0 correlation=0.60 what=[Accept this PIV and output] noise=0.20 threshold=5 c1=3 c2=1 save=["+dirOut+"PIV_"+t+"_"+t1+".txt]");

			selectWindow(t+"_"+t1+"_PIV1");
			run("Close");
			selectWindow("Scale Graph");
			run("Close");
			selectWindow(t+"_"+t1);
			run("Close");
		}

		for(t=1;t<fram;t++) {
			t1=t+1;
			run("plot...", "select=["+dirOut+"PIV_"+t+"_"+t1+".txt] vector_scale=1 max=15 plot_width=0 plot_height=0 show draw lut=S_Pet");
				if(t!=(fram-1)){
					selectWindow("Scale Graph");
					run("Close");
				}
		}

		// save scale graph (=color legend)

		selectWindow("Scale Graph");
		saveAs("Tiff",dirOut+"Scale_Graph.tif");
		run("Close");

		// save stack with channel 1 vectors, channel 2 heatmap, over time
		run("Images to Stack", "name=Stack title=[] use");
		n=nSlices()/2;

		run("Stack to Hyperstack...", "order=xyczt(default) channels=1 slices=2 frames="+n+" display=Color");
		selectWindow("Stack");
		saveAs("Tiff",dirOut+"FlowMap.tif");
		run("Close");

		run("Close All");
	}
}