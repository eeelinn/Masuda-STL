//To be called by the Count_NP_Cells.ijm macro
//make sure to select the image to process/count

	imageTitle = getTitle();

//Invokes Colour Deconvolution plugin and deletes the third, unused colour (green)
	selectWindow(imageTitle);
	run("Colour Deconvolution", "vectors=[H&E]");
	purpleImage = imageTitle + "-(Colour_1)";
	pinkImage = imageTitle + "-(Colour_2)";
	selectWindow(imageTitle + "-(Colour_3)");
	close();

//Working with the pink image, duplicate and create a mask
	selectWindow(pinkImage);
	run("Duplicate...", "title=pinkCopy");
	pinkCopy = getTitle();
	processColor(pinkCopy);

	run("Remove Outliers...", "radius=2 threshold=50 which=Dark");
	run("Remove Outliers...", "radius=50 threshold=50 which=Bright");
	run("Create Selection");

//Work with purple image
	selectWindow(purpleImage);
	processColor(purpleImage);
	run("Remove Outliers...", "radius=20 threshold=50 which=Dark");
	run("Remove Outliers...", "radius=10 threshold=50 which=Bright");
	run("Restore Selection");
	setForegroundColor(255, 255, 255);
	run("Fill", "slice");
	run("Create Selection");

//Work with original pink image
	selectWindow(pinkImage);
	processColor(pinkImage);
	run("Restore Selection");
	//run("Make Inverse");
	run("Fill", "slice");
	run("Create Selection");
	roiManager("Add");

//Final Touches
	selectWindow(imageTitle);
	run("From ROI Manager");
	setTool("freehand");
	waitForUser("Select Areas", "Please draw around the area you want to exclude. Hold 'Shift' for multiple areas. Then Click 'OK'.");
	run("Remove Overlay");

	selectWindow(pinkImage);
	run("Restore Selection");
	run("Fill", "slice");
	roiManager("Select", 0);
	roiManager("Deselect");
	roiManager("Delete");
	run("Select None");
	run("Watershed");

	run("Analyze Particles...", "size=16-4000 show=Masks display summarize");

//Show Results Overlayed on Original Image
	selectWindow("Mask of " + pinkImage);
	run("Create Selection");
	roiManager("Add");
	selectWindow(imageTitle);
	run("From ROI Manager");

//Clean Up
	selectWindow(pinkCopy);
	close();
	selectWindow(purpleImage);
	close();
	selectWindow("ROI Manager");
	run("Close"); 
	selectWindow(pinkImage);
	close();

//Maybe add a Save option?


//Increase Contrast of Image [Function]

function processColor(imageTitle) {
	selectWindow(imageTitle);
	run("Enhance Contrast...", "saturated=50");
	setAutoThreshold("Otsu");
	setOption("BlackBackground", false);
	run("Convert to Mask");
}
	
