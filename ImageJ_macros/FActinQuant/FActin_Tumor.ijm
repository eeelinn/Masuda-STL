image = getTitle();
print(image);
run("Duplicate...", "title=Selected");

//remove scale bar
selectWindow(image);
makeRectangle(1689, 1140, 231, 60);
run("Clear", "slice");
run("Select None");
run("Duplicate...", "title=Copy");

run("Split Channels");
selectWindow("Copy (red)");
close();
selectWindow("Copy (blue)");
close();
selectWindow("Copy (green)");

setAutoThreshold("Otsu dark");
setOption("BlackBackground", false);
run("Convert to Mask");

run("Fill Holes");
run("Create Selection");
selectWindow(image);
run("Restore Selection");

run("Set Measurements...", "area mean standard integrated display redirect=image decimal=5");
run("Measure");
run("Restore Selection");
run("Make Inverse");
run("Measure");
selectWindow("Copy (green)")
close();

selectWindow("Selected");
run("Restore Selection");


