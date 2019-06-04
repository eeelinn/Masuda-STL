#@File (label='Choose file to analyze') file
#@File(label='Choose a save directory', style='directory') save_Dir
#@ Short(label='# of Slices', min=1) split

import os, csv
from ij.gui import Roi, Overlay, TextRoi
from ij.plugin import ChannelSplitter
from java.awt import Font, Color
from loci.plugins import BF
from ij import IJ, ImageStack, WindowManager
from loci.common import Region
from loci.plugins.in import ImporterOptions, ImagePlusReader, ImportProcess

def Analyze(imp):
	IJ.setAutoThreshold(imp, "Otsu dark stack")
	IJ.run(imp, "Convert to Mask", "method=MaxEntropy background=Dark calculate black")
	IJ.run(imp, "Despeckle", "stack")
	IJ.run(imp, "Watershed", "stack")
	IJ.run(imp, "Analyze Particles...", "size=8-Infinity pixel show=Masks summarize stack")

def saveImg(imp, nslices):
	mask = WindowManager.getImage('Mask of ' + imp.getTitle())
	IJ.save(mask, saveIm + '/' + title + '_' + str(i+1) + '.tif')
	label = mask.duplicate()
	for n in range(1,nslices+1):
		s = label.getStack().getProcessor(n);
		s.setFont(Font("SansSerif", Font.BOLD, 30));
		s.setColor(Color.blue);
		s.drawString(title + ' Layer: ' + str(i+1) + ' Slice: ' + str(n), 20, 40)
	label.updateAndDraw()
	IJ.save(label, saveIm + '/labeled_' + title + '_' + str(i+1) + '.tif')
	IJ.run("Close")

def fileProcess(title):
	#save Summary Window and close
	IJ.selectWindow("Summary of " + title)	
	tempFile = saveDir + "/temp_" + title + str(i)+ ".csv"
	IJ.saveAs("Results", tempFile)
	
	#open data in string for final file save
	with open(tempFile, 'r') as r:
		result = r.read().splitlines()
	return result[1:]
	

# Get file name and path
filename = file.getAbsolutePath()
saveName = os.path.basename(filename)
saveDir = str(save_Dir) + '/Results'
saveIm = str(save_Dir) + '/CountedImages'

# Initialize variables for Saving
name = ['File']
layer = ['Layer']
results = ['Slice,Count,Total Area,Average Size,%Area']

# Check if folders are there or not   
if not os.path.exists(saveDir):     
	os.mkdir(saveDir)
if not os.path.exists(saveIm):    	
	os.mkdir(saveIm)

# set up options for import
opts = ImporterOptions()
opts.setId(filename)
opts.setUngroupFiles(True)

# set up import process
process = ImportProcess(opts)
process.execute()
nseries = process.getSeriesCount()

# Channel Splitter Definition
splitter = ChannelSplitter()
 
# reader belonging to the import process
reader = process.getReader()
 
# reader external to the import process
impReader = ImagePlusReader(process)

# loop through all series in file
for i in range(0, nseries):
	print "%d/%d %s" % (i+1, nseries, process.getSeriesLabel(i)[10:])
     
	# activate series (same as checkbox in GUI)
	opts.setSeriesOn(i,True)
 
	# point import process reader to this series
	reader.setSeries(i)
 
	# read and process all images in series
	imps = impReader.openImagePlus()

	# deactivate series for next round (otherwise will re-analyze everything)
	opts.setSeriesOn(i, False)

	# run analysis on active series for all images in stack
	for imp in imps:
		#title = imp.getTitle()
		#imp.show()
		channels = splitter.split(imp)
		
		# int array [width, height, nChannels, nSlices, nFrames]
		Dim = imp.getDimensions()
		for c in channels:
			title = c.getTitle()
			for i in range(split):
				titles = [title]*Dim[3]
				name.extend(titles)
				layer.extend([i+1]*Dim[3])
			
				# Set up ROIs and analyze based on how it is split
				c.setRoi(0, i*Dim[1]/split, Dim[0], Dim[1]/split)
				Analyze(c)
				saveImg(c, Dim[3])
			
			# save results of series
			results.extend(fileProcess(title))

#IJ.run("Close All")

# concatenate all excel files into one file
with open(saveDir + '/' + saveName + '.csv', 'w') as w:
	w.write('\n'.join('%s,%s,%s' % x for x in zip(name, layer, results)))

# Remove temporary .csv files
for fname in os.listdir(saveDir):
    if fname.startswith("temp_"):
        os.remove(os.path.join(saveDir, fname))


#TODO: close summary table



