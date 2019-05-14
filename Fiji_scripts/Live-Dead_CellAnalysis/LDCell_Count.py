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
results = ['Slice,Count,Total Area,Average Size,%Area']

def Analyze(imp):
	IJ.setAutoThreshold(imp, "Otsu dark stack")
	IJ.run(imp, "Convert to Mask", "method=MaxEntropy background=Dark calculate black")
	IJ.run(imp, "Despeckle", "stack")
	IJ.run(imp, "Watershed", "stack")
	IJ.run(imp, "Analyze Particles...", "size=8-Infinity pixel show=Masks summarize stack")

def fileProcess(title):
	#save Summary Window
	IJ.selectWindow("Summary of " + title)	
	tempFile = saveDir + "/" + title + str(i)+ ".csv"
	IJ.saveAs("Results", tempFile)
	#open data in string for final file save
	with open(tempFile) as r:
		result = r.read().splitlines()
	return result[1:]

# Get file name and path
filename = file.getAbsolutePath()
saveName = os.path.basename(filename)
dirPath = os.path.dirname(filename)

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
		print Dim

		for i in range(split):
			titles = [title]*Dim[2]*Dim[3]
			name.extend(titles)
			layer.extend([i+1]*Dim[2]*Dim[3])
			
			# Set up ROIs and analyze based on how it is split
			imp.setRoi(0, i*Dim[1]/3, Dim[0], Dim[1]/3)
			Analyze(imp)

		opts.setSeriesOn(i, False)


	# save results of series
	saveDir = "C:/Users/Erikka Linn/Documents/Masuda Lab/Test"
	results.extend(fileProcess(title))


# concatenate all excel files into one file
with open(saveDir + '/' + saveName + '.csv', 'w') as w:
	w.write('\n'.join('%s,%s,%s' % x for x in zip(name, layer, results)))






