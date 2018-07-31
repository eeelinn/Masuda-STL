//Name: FActin_v2.ijm
//Author: Erikka Linn
//Version: 2.1
//Last Date Modified: 7.31.2018 JST
//Use: Automatically selects and measures intensity of actin
//in cells



//BEFORE YOU RUN
//Calibrate the size of the image to the scale bar with "Set Scale"

MinParticle = 90;		//Min particle area to be included



//The rest is automated, comments describe what happens

//Set Measurements and Duplicate original image for processing
run("Options...", "iterations=1 count=1 edm=8-bit");
run("Set Measurements...", "area mean standard integrated display redirect=None decimal=5");
original = getImageID();
run("Duplicate...", " ");
title = getTitle();
print(title);
image = getImageID();

//Split RGB image by color channels
run("Split Channels");
selectWindow(title + " (blue)");
Blue = getImageID();
selectWindow(title + " (green)");
Green = getImageID();

//Select Scale bar to remove
selectWindow(title + " (red)");
setAutoThreshold("Minimum dark");
setOption("BlackBackground", false);
run("Convert to Mask");
run("Create Selection");
close();

//Normalize/subtract background of image to be analyzed for intensity
selectImage(Green);
run("Restore Selection");
run("Clear", "slice");
run("Select None");
run("Subtract Background...", "rolling=1500");
run("Duplicate..."," ");
toAnalyze = getImageID();

//Remove the scale bar
selectImage(Blue);
run("Restore Selection");
run("Clear", "slice");
run("Select None");

//Select and split image by nuclei
run("Gaussian Blur...", "sigma=25");
run("Find Maxima...", "noise=20 output=[Segmented Particles]");
run("Smooth");
run("Invert");
run("Multiply...", "value=25");
run("Make Binary");
Segment = getImageID();
selectImage(Blue);
close();

//select Actin Area
selectImage(Green);
run("Gaussian Blur...", "sigma=5");
//setThreshold(LowThreshold, HighThreshold);
run("Make Binary");
run("Close-");
run("Fill Holes");

//Split actin area by selected nuclei/cells
imageCalculator("Subtract create", Green, Segment);
run("Open");
toProcess = getImageID();
selectImage(Green);
close();

//Move selected area to image, split into cells and anaylze intensity of each
selectImage(toProcess);
run("Analyze Particles...", "size="+MinParticle+"-Infinity show=Masks");
run("Create Selection");
roiManager("reset");
roiManager("Add");
roiManager("Split");
roiManager("Select", 0);
roiManager("Delete");
roiManager("Sort");
selectImage(toAnalyze);
roiManager("Show All");
roiManager("Measure");
selectImage(Segment);
close();

//Display selection on original image
selectImage(original);
roiManager("Show All");
