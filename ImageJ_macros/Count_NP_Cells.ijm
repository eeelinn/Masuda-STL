//Cell Counting Macro v1.5 for Slink by Erikka Linn

//Make sure pictures are at 4x magnification
//Before you run, go to analyze > set scale to change from pixels 

//add part to open specific pictures... (do this later) but for now 
//allow user to choose what kind of counting to do, different ones 
//because non-punctured NP cells tend to be much larger

Punc = "Punctured NP Cells";
NonPunc = "Non-Punctured NP Cells";

choices = newArray(Punc, NonPunc);
Dialog.create("Image Type");
Dialog.addChoice("Tissue Sample", choices);
Dialog.show();
Result = Dialog.getChoice();

//ran macro based off option chosen
runMacro(Result);
