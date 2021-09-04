// Batch bleach correction
// acquisition set up: images collected in channel 2 -> w2CSU, exc 488 nm -> -488, em 525-30
// input : list_files.csv containing the name without extension of each .nd file (column name: movie)
// output : bleach-corrected movies

input_path = getDirectory("Input directory: ");
// directory containing the list_files.csv file and the .nd/.tiff files - name sequence with <moviename>_w2CSU-488-Em-525-30_t<timepoint>.tiff
output_path = getDirectory("Output directory: ");

setBatchMode(true);

if(isOpen("Results")==true) {
	selectWindow("Results");
	run("Close");
}

open(input_path+"list_files.csv");

IJ.renameResults("list_files.csv","Results");


for (i = 0; i < nResults ; i++) {

	file = getResultString("movies", i);
	print(file);

	run("Image Sequence...", "open=" + input_path + " file="+file+"_w2CSU-488-Em-525-30_t" + " sort");

	rename(file);

	run("Bleach Correction", "correction=[Simple Ratio]");

	selectWindow(file);
	close();

	selectWindow("DUP_"+file);
	saveAs("tiff", output_path+file+"_bleach-corr.tif");

	run("Close All");
}

run("Close All");

run("Clear Results");