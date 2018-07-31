//Title: Batch Counting IHC
//Ver. 1 ORS_20170828
//Author: Erikka Linn
//NOTE: Before counting, please go to Analyze>>Set Scale and set the scale for image in pixels/um. Check "global" to maintain the same scale for all the images.

input = getDirectory("Input directory");	//Folder with images you want counted
output = getDirectory("Output directory");  //Folder where you want to save the new data (saves image of positive and total cells each)
keyword = "5HT";				//Keyword in the file names that you want (in case there are other photos in the folder)
suffix = ".tif";  					//Works with tiff images

processFolder(input);
waitForUser("Batch Completed", "Batch Counting IHC has finished. Thank you for using!");

//process through the folder, looks for images with the keyword specified
function processFolder(input) {
    list = getFileList(input);
    for (i = 0; i < list.length; i++) {
        
        if(File.isDirectory(input + list[i])) {   //if it's a directory, go to subfolder
	processFolder("" + input + list[i]);
        }
        if(endsWith(list[i], suffix)&&indexOf(list[i],keyword) >= 0) {
	processImage(input, output, list[i]);
        }
    }
}

function processImage(input, output, image) {
	print("Processing: " + input + image);
	open(input + image);  //open image
	countBrownCells(image, output);
	countTotalCells(image, output);
	print("Finished counting: " + input + image);	
}

//Invokes Colour Deconvolution plugin and deletes the third, unused colour (green)
function splitColours(imageTitle) {
	print("Splitting image to brown and blue");
	selectWindow(imageTitle);
	run("Set Measurements...", "area limit redirect=None decimal=3");
	run("Colour Deconvolution", "vectors=[H DAB]");
	selectWindow(imageTitle + "-(Colour_3)");
	close();
}

//Counts the positive cells, if satisfied click 'Yes', if not click 'No' to redo the counting of the positive cells
function countBrownCells(imageTitle, output) {
	splitColours(imageTitle);
	selectWindow(imageTitle + "-(Colour_2)");
	run("8-bit");
	run("Invert");
	
	setTool("freehand");
	waitForUser("Select Areas", "Please draw around the area you want to exlude. Hold 'Shift' for multiple areas. Then Click 'OK'.");
	selectWindow(imageTitle + "-(Colour_2)");
	roiManager("Add");
	run("Clear", "slice");
	roiManager("Deselect");
	run("Select All");

	run("Subtract...", "value=50");
	setAutoThreshold("Default dark");
	
	// Thresholding. Try and cover as much as you can, to the point of over estimating.
	run("Threshold...");
	setOption("BlackBackground", false);
	waitForUser("Thresholding", "Please drag the red threshold until you have covered the objects you want to include as precise as you can. Then Click 'OK'.");

	print("Counting positive cells...");
	selectWindow(imageTitle + "-(Colour_2)");
	run("Convert to Mask");
	run("Close-");
	run("Fill Holes");
	run("Watershed");
	run("Analyze Particles...", "size=6.39-136.97 show=[Overlay Masks] display exclude clear summarize");
	if(isOpen("Results")) {
		selectWindow("Results");
	}
	waitForUser("Copy Area", "Copy the areas in the results window to your Excel document");

	//saves positive image
	if(getBoolean("Do you want to save the image?")) {
		print("Saving image of positive cells...");
		selectWindow(imageTitle + "-(Colour_2)");
		saveAs("tiff", output + imageTitle + "_positive.tif");
		print("Saved " + imageTitle + "_positive.tif to " + output);
	}
	else {
		print("Redoing...");
		roiManager("Delete");
		if(isOpen("Results")) {
			selectWindow("Results");
			run("Close");
		}
		selectWindow(imageTitle);
		close("\\Others");
		countBrownCells(imageTitle, output);
	}
	if(isOpen("Results")) {
		selectWindow("Results");
		run("Close");
	}
}

//Counts the total cells, if satisfied click 'Yes', if not click 'No' to redo the counting of the total cells
function countTotalCells(imageTitle, output) {
	selectWindow(imageTitle + "-(Colour_1)");
	run("8-bit");
	run("Invert");
	run("Subtract...", "value=20");
	roiManager("Select", 0);
	setBackgroundColor(0, 0, 0);
	run("Clear", "slice");
	roiManager("Deselect");
	run("Select All");

	setAutoThreshold("Default dark");
	run("Threshold...");
	waitForUser("Threshold the nuclei", "Drag the red threshold until you have around the same percentage value. Click 'OK' when ready.");
	print("Counting total cells...");
	selectWindow(imageTitle + "-(Colour_1)");
	run("Convert to Mask");
	run("Close-");
	run("Fill Holes");
	run("Watershed");
	run("Set Measurements...", "limit redirect=None decimal=3");
	run("Analyze Particles...", "size=3.42-136.97 show=[Overlay Masks] exclude summarize");
	
	//saves total cells image
	if(getBoolean("Do you want to save the image?")) {
		print("Saving image of total cells...");
		selectWindow(imageTitle + "-(Colour_1)");
		saveAs("tiff", output + imageTitle + "_total.tif");
		print("Saved " + imageTitle + "_total.tif to " + output);
		run("Close All");
		roiManager("Delete");
	}
	else {
		print("Redoing...");
		selectWindow(imageTitle);
		close(imageTitle + "-(Colour_1)");
		splitColours(imageTitle);
		close(imageTitle + "-(Colour_2)");
		countTotalCells(imageTitle, output);
	}
}

