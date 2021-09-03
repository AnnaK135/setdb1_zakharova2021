 /*
* ImgageJ macro
* This macro performs backgroung subtraction using the “rolling ball” method
* and splits channels for the multi-channel images.
*
*To customize settings:
* enter the paths to the image folders in your system;
* after the first run adjust the rolling ball radius "rolling=" in the function split_subtract so that it best fits your images.
*/
 
 while (nImages>0) { 
          selectImage(nImages); 
          close(); 
      } 

inputDAPI = "path_to_the_folder_with_dapi_stained_images"; 
listDAPI = getFileList(inputDAPI);
inputPHL = "path_to_the_folder_with_phl_stained_images"; 
listPHL = getFileList(inputPHL);

for (i = 0; i < listPHL.length; i++){
	print(listPHL[i]);
}

function split_subtract(input, filename) {
	open(input+ filename);
	title = getTitle();
	run("Subtract Background...", "rolling=50");
	run("Split Channels");
	selectImage(title + " (red)");
	close();
	selectImage(title + " (blue)");
	close();
}

function split(input, filename) {
	open(input+ filename);
	title = getTitle();
	run("Split Channels");
	selectImage(title + " (red)");
	close();
	selectImage(title + " (green)");
	close();
}

for (i = 0; i < listPHL.length; i++){
	split_subtract(inputPHL, listPHL[i]);
}

for (i = 0; i < listDAPI.length; i++){
	split(inputDAPI, listDAPI[i]);
}


