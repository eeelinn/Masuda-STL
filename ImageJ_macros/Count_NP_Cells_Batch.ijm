//Cell Counting Macro v1.5 for Slink by Erikka Linn

//Make sure pictures are at 4x magnification
//Before you run, go to analyze > set scale to change from pixels 

//add part to open specific pictures... (do this later) but for now 
//allow user to choose what kind of counting to do, different ones 
//because non-punctured NP cells tend to be much larger

Dialog.create("Input Keyword");
Dialog.addString("Keyword: ", "<input text>");
Dialog.show();

input = getDirectory("Input directory");    //Folder with images you want counted
keyword = Dialog.getString();	    //Keyword in the file names that you want (in case there are other photos in the folder)
suffix = ".jpg";  			    //Works with tiff images

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
	processImage(input, list[i]);
        }
    }
}

function processImage(input, image) {
	print("Processing: " + input + image);
	open(input + image);  //open image

	Punc = "Punctured NP Cells";
	NonPunc = "Non-Punctured NP Cells";

	choices = newArray(Punc, NonPunc);
	Dialog.create("Image Type");
	Dialog.addChoice("Tissue Sample", choices);
	Dialog.show();
	Result = Dialog.getChoice();

	//run macro based off option chosen
	runMacro(Result);
}
