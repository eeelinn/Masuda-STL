#@File (label='Choose file to analyze') file
#@File(label='Choose a save directory', style='directory') save_Dir
#@Integer(label="remove first __ slices", value=5) front
#@Integer(label="remove last __ slices", value=5) back
#@Output string sumtext

import os, csv
from ij.gui import Roi, Overlay, TextRoi
from ij.plugin import ChannelSplitter
from java.awt import Font, Color
from loci.plugins import BF
from ij import IJ, ImageStack, WindowManager, ImagePlus
from loci.common import Region
from loci.plugins.in import ImporterOptions, ImagePlusReader, ImportProcess


def Analyze(imp):
	IJ.setAutoThreshold(imp, "Otsu Dark stack")
	IJ.run(imp, "Convert to Mask", "method=MaxEntropy background=Dark calculate black")
	#IJ.run(imp, "Invert", "stack")
	IJ.run(imp, "Despeckle", "stack")
	IJ.run(imp, "Watershed", "stack")
	IJ.run(imp, "Analyze Particles...", "size=8-Infinity pixel show=Masks summarize stack")

def sliceCrop(stack, start, end):
	for i in range(0, start):
		stack.getStack().deleteSlice(1)
	for i in range(0, end):
		stack.getStack().deleteLastSlice()
	return stack

def saveImg(imp, nslices, label):
	mask = WindowManager.getImage('Mask of ' + imp.getTitle())
	IJ.save(mask, saveDir + '/' + title + '_' + label + '.tif')
	labeled = mask.duplicate()
	for n in range(1,nslices+1):
		s = labeled.getStack().getProcessor(n);
		s.setFont(Font("SansSerif", Font.BOLD, 30));
		s.setColor(Color.blue);
		s.drawString(title + ' Layer: ' + label + ' Slice: ' + str(n), 20, 40)
	labeled.updateAndDraw()
	IJ.save(labeled, saveDir + '/labeled_' + title + '_' + label + '.tif')
	IJ.run("Close")

def fileProcess(title):
	#save Summary Window and close
	IJ.selectWindow("Summary of " + title)	
	tempFile = saveDir + "/temp_" + title + str(i)+ ".csv"
	IJ.saveAs("Results", tempFile)
	IJ.run("Close")
	count = []
	
	# open data in string for final file save
	with open(tempFile, 'r') as r:
		result = r.read().splitlines()
		for n in range(1, len(result)):
			array = result[n].split(',')
			count.append(int(array[1]))

	# delete temp file and return
	os.remove(tempFile)
	return result[1:], count
	

# Get file name and path
filename = file.getAbsolutePath()
saveName = os.path.basename(filename)
saveDir = str(save_Dir) + '/Results_' + saveName

layers = [0.235, 0.315, 0.45]
labels = ["Top", "Middle", "Bottom"]

# Initialize variables for Saving
name = ['File']
layer = ['Layer']
results = ['Slice,Count,Total Area,Average Size,%Area']
summary = {"Top": [], "Middle": [], "Bottom": []}


# Check if folders are there or not   
if not os.path.exists(saveDir):     
	os.mkdir(saveDir)
	
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
		channels = splitter.split(imp)
		
		for c in channels:
			title = c.getTitle()
			c = sliceCrop(c, front, back)
			
			# int array [width, height, nChannels, nSlices, nFrames]
			Dim = c.getDimensions()
			prev = 0
			if len(channels) > 1:
				#if two channels, care about nSlices
				d_idx = 3
			else:
				#if only one channel, care about nFrames
				d_idx = 4
				
			for i in range(0, len(layers)):
				titles = [title]*Dim[d_idx]
				name.extend(titles)
				layer.extend([labels[i]]*Dim[d_idx])
			
				# Set up ROIs and analyze based on how it is split
				c.setRoi(0, int(prev*Dim[1]), Dim[0], int(layers[i]*Dim[1]))
				Analyze(c)
				saveImg(c, Dim[d_idx], labels[i])
				
				# save results of series
				prev = prev + layers[i]
				all, count = fileProcess(title)
				summary[labels[i]].append(sum(count))
				results.extend(all)
			

# prepare summary
if len(channels) > 1:
	sumtext = 'Summary: {0}\nLayer,Live,Dead,Viability(%)\n'.format(saveName)
	tLive = 0.0
	tDead = 0.0
	for key in labels:
		live = float(summary[key][0])
		tLive += live
		dead = float(summary[key][1])
		tDead += dead
		if live + dead == 0:
			viability = 'NA'
		else:
			viability = live / (live + dead) * 100
		sumtext += '{0},{1},{2},{3}\n'.format(key, live, dead, viability)
	sumtext += 'Total,{0},{1},{2}\n'.format(tLive, tDead, tLive/(tLive + tDead)*100)
else:
	sumtext = 'Summary: {0}\nLayer,Number of Cells\n'.format(saveName)
	tCells = 0.0
	for key in labels:
		cells = float(summary[key][0])
		tCells += cells
		sumtext += '{0},{1}\n'.format(key, cells)
	sumtext += 'Total,{0}\n'.format(tCells)


# concatenate all excel files into one file
with open(saveDir + '/' + saveName + '.csv', 'w') as w:
	w.write(sumtext)
	w.write('\nRaw Data\n')
	w.write('\n'.join('%s,%s,%s' % x for x in zip(name, layer, results)))

# add to the log file
with open(str(save_Dir) + '/summary.csv', 'a+') as s:
	s.write(sumtext)

print("Script completed successfully!")
