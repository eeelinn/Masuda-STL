#@File file

import os, csv
from ij.measure import ResultsTable, Measurements
from ij.gui import Roi
from ij.plugin import ChannelSplitter
from ij.plugin.frame import RoiManager
from loci.plugins import BF
from ij import IJ, ImageStack
from loci.common import Region
from loci.plugins.in import ImporterOptions, ImagePlusReader, ImportProcess

name = ['File']
layer = ['Layer']
split = 3

# Get file name and path
filename = file.getAbsolutePath()
dirPath = os.path.dirname(filename)
print os.path.realpath(filename)

# Check if folders are there or not   
if not os.path.exists(dirPath + '/Results'):     
	os.mkdir(dirPath + '/Results')

# set up options for import
opts = ImporterOptions()
opts.setId(filename)
opts.setUngroupFiles(True)

# set up import process
process = ImportProcess(opts)
process.execute()
nseries = process.getSeriesCount()
 
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

	# run analysis on active series for all images in stack
	for imp in imps:
		title = imp.getTitle()
		imp.show()
		# int array [width, height, nChannels, nSlices, nFrames]
		Dim = imp.getDimensions()

		for i in range(split):
			titles = [title]*Dim[2]*Dim[3]
			name.extend(titles)
			layer.extend([i+1]*Dim[2]*Dim[3])
			
			# Set up ROIs to analyze from (split into 1/3 portions)
			imp.setRoi(0, i*Dim[1]/3, Dim[0], Dim[1]/3)
		
			IJ.setAutoThreshold(imp, "Otsu dark stack")
			IJ.run(imp, "Convert to Mask", "method=MaxEntropy background=Dark calculate black")
			IJ.run(imp, "Despeckle", "stack")
			IJ.run(imp, "Watershed", "stack")
			IJ.run(imp, "Analyze Particles...", "size=8-Infinity pixel show=Masks summarize stack")
		opts.setSeriesOn(i, False)


	# save results
	saveDir = "C:/Users/Erikka Linn/Documents/Masuda Lab/Test"
	IJ.selectWindow("Summary of " + title)	
	IJ.saveAs("Results", saveDir + "/" + title + str(i)+ ".csv")
	break;


# concatenate all excel files into one file
print name, layer
with open(saveDir + '/names.csv', 'w') as f:
	writer = csv.writer(f, delimiter=',')
	writer.writerows(zip(name, layer))

#os.system("cat " + saveDir + "/*.csv > C:/Users/Erikka Linn/Documents/Masuda Lab/Results.csv") 






