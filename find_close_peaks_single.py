# Usage: Run plugin and open input image when prompted.
# Output will be displayed.
# KNOWN ISSUES: An erroneous peak is always identified at (0,0)
# TODO: User entry of label names

from ij import IJ, ImagePlus, ImageStack
from ij.plugin import ZProjector
from ij.plugin.filter import RankFilters
# from ij.plugin.filter import BackgroundSubtracter
import net.imagej.ops
from net.imglib2.view import Views
from net.imglib2.img.display.imagej import ImageJFunctions as IL
from net.imglib2.algorithm.dog import DogDetection
from ij.gui import PointRoi
from jarray import zeros
from ij.measure import ResultsTable
from math import sqrt
from java.awt import Color
from ij.plugin.frame import RoiManager
from ij.gui import GenericDialog

def distance(peak_1, peak_2):
	return sqrt((peak_2[1] - peak_1[1]) * (peak_2[1] - peak_1[1]) + (peak_2[0] - peak_1[0]) * (peak_2[0] - peak_1[0]))

# edited for Alondra Burguete's defaults
# Supports different peak height by channel

def getOptions(): # in pixels
	gd = GenericDialog("Options")
	gd.addNumericField("Channel for FUS", 3, 0)
	gd.addNumericField("Channel for DNAJB6", 2, 0)
	#gd.addNumericField("radius_background", 100, 0)
 	gd.addNumericField("sigmaSmaller", 3, 0)
 	gd.addNumericField("sigmaLarger", 10, 0)
  	gd.addNumericField("minPeakValue FUS", 40, 0)
  	gd.addNumericField("minPeakValue DNAJB6", 15, 0)
  	gd.addNumericField("min_dist", 1, 0)
  	gd.showDialog()
	Channel_1 = gd.getNextNumber()
	Channel_2 = gd.getNextNumber()
	#radius_background = gd.getNextNumber()
  	sigmaSmaller = gd.getNextNumber()
  	sigmaLarger = gd.getNextNumber()
  	minPeakValueCh1 = gd.getNextNumber()
  	minPeakValueCh2 = gd.getNextNumber()
  	min_dist = gd.getNextNumber()

  	# return int(Channel_1), int(Channel_2), radius_background, sigmaSmaller, sigmaLarger, minPeakValueCh1, minPeakValueCh2, min_dist
	return int(Channel_1), int(Channel_2), sigmaSmaller, sigmaLarger, minPeakValueCh1, minPeakValueCh2, min_dist

def extract_channel(imp_max, Channel_1, Channel_2):

	stack = imp_max.getImageStack()
	ch_1 = ImageStack(imp_max.width, imp_max.height)
	ch_1.addSlice(str(Channel_1), stack.getProcessor(Channel_1))

	ch_2 = ImageStack(imp_max.width, imp_max.height)
	ch_2.addSlice(str(Channel_2), stack.getProcessor(Channel_2))

	ch1 = ImagePlus("FUS" + str(Channel_1), ch_1)
	ch2 = ImagePlus("DNAJB6" + str(Channel_2), ch_2)

	ch1_1 = ch1.duplicate()
	ch2_1 = ch2.duplicate()

	ip1 = ch1_1.getProcessor().convertToFloat()
	ip2 = ch2_1.getProcessor().convertToFloat()

	return ip1, ip2

# Background subtraction
def back_subtraction(ip1, ip2, radius_background):
	bgs=BackgroundSubtracter()
	bgs.rollingBallBackground(ip1, radius_background, False, False, True, True, True)
	bgs.rollingBallBackground(ip2, radius_background, False, False, True, True, True)

	imp1 = ImagePlus("ch1 back sub", ip1)
	imp2 = ImagePlus("ch2 back sub", ip2)

	IJ.run(imp1, "Enhance Contrast", "saturated=0.35")
	IJ.run(imp2, "Enhance Contrast", "saturated=0.35")
	return imp1, imp2

def find_peaks(imp1, imp2, sigmaSmaller, sigmaLarger, minPeakValueCh1, minPeakValueCh2):
	# FIND PEAKS
	# sigmaSmaller ==> Size of the smaller dots (in pixels)
	# sigmaLarger ==> Size of the bigger dots (in pixels)
	# minPeakValue ==> Intensity above which to look for dots
	
	# Preparation FUS channel
	ip1_1 = IL.wrapReal(imp1)
	ip1E = Views.extendMirrorSingle(ip1_1)
	imp1.show()

	#Preparation DNAJB6 channel
	ip2_1 = IL.wrapReal(imp2)
	ip2E = Views.extendMirrorSingle(ip2_1)
	imp2.show()

	calibration = [1.0 for i in range(ip1_1.numDimensions())]
	extremaType = DogDetection.ExtremaType.MINIMA
	normalizedMinPeakValue = False

	dog_1 = DogDetection(ip1E, ip1_1, calibration, sigmaSmaller, sigmaLarger,
	  				   extremaType, minPeakValueCh1, normalizedMinPeakValue)

	dog_2 = DogDetection(ip2E, ip2_1, calibration, sigmaSmaller, sigmaLarger,
	  				   extremaType, minPeakValueCh2, normalizedMinPeakValue)

	peaks_1 = dog_1.getPeaks()
	peaks_2 = dog_2.getPeaks()

	return ip1_1, ip2_1, peaks_1, peaks_2

def run():

	IJ.run("Close All", "")
	IJ.log("\\Clear")

	IJ.log("Find_close_peaks")

	imp = IJ.run("Bio-Formats Importer")
	imp = IJ.getImage()


	#Channel_1, Channel_2, radius_background, sigmaSmaller, sigmaLarger, minPeakValueCh1, minPeakValueCh2, min_dist = getOptions()
	Channel_1, Channel_2, sigmaSmaller, sigmaLarger, minPeakValueCh1, minPeakValueCh2, min_dist = getOptions()
	

	IJ.log("options used:" \
    		+ "\n" + "channel 1:" + str(Channel_1) \
    		+ "\n" + "channel 2:"+ str(Channel_2) \
    		# + "\n" + "Radius Background:"+ str(radius_background) \
    		+ "\n" + "Smaller Sigma:"+ str(sigmaSmaller) \
    		+ "\n" + "Larger Sigma:"+str(sigmaLarger) \
    		+ "\n" + "Min Peak Value Ch1:"+str(minPeakValueCh1) \
			+ "\n" + "Min Peak Value Ch2:"+str(minPeakValueCh2) \
    		+ "\n" + "Min dist between peaks:"+str(min_dist))

	IJ.log("Computing Max Intensity Projection")

	if imp.getDimensions()[3] > 1:
		imp_max = ZProjector.run(imp,"max")
		#imp_max = IJ.run("Z Project...", "projection=[Max Intensity]")
		#imp_max = IJ.getImage()
	else:
		imp_max = imp

	ip1, ip2 = extract_channel(imp_max, Channel_1, Channel_2)
	imp1 = ImagePlus("ch1", ip1)
	imp2 = ImagePlus("ch2", ip2)
	# imp1, imp2 = back_subtraction(ip1, ip2, radius_background)
	imp1.show()
	imp2.show()

	IJ.log("Finding Peaks")

	ip1_1, ip2_1, peaks_1, peaks_2 = find_peaks(imp1, imp2, sigmaSmaller, sigmaLarger, minPeakValueCh1, minPeakValueCh2)

	# Create a PointRoi from the DoG peaks, for visualization
	roi_1 = PointRoi(0, 0)
	roi_2 = PointRoi(0, 0)
	roi_3 = PointRoi(0, 0)
	roi_4 = PointRoi(0, 0)

	# A temporary array of integers, one per dimension the image has
	p_1 = zeros(ip1_1.numDimensions(), 'i')
	p_2 = zeros(ip2_1.numDimensions(), 'i')

	# Load every peak as a point in the PointRoi
	for peak in peaks_1:
	  # Read peak coordinates into an array of integers
	  peak.localize(p_1)
	  roi_1.addPoint(imp1, p_1[0], p_1[1])

	for peak in peaks_2:
	  # Read peak coordinates into an array of integers
	  peak.localize(p_2)
	  roi_2.addPoint(imp2, p_2[0], p_2[1])

# TS updated to correct the peak set
	for peak_1 in peaks_1:
		peak_1.localize(p_1)
		for peak_2 in peaks_2:
			peak_2.localize(p_2)
			d1 = distance(p_1, p_2)
			if  d1 < min_dist:
				#roi_3.addPoint(imp1, p_2[0], p_2[1])
				roi_3.addPoint(imp1, p_1[0], p_1[1])
				break

	for peak_2 in peaks_2:
		peak_2.localize(p_2)
		for peak_1 in peaks_1:
			peak_1.localize(p_1)
			d2 = distance(p_2, p_1)
			if  d2 < min_dist:
				roi_4.addPoint(imp1, p_2[0], p_2[1])
				break

	rm = RoiManager.getInstance()
	if not rm:
	  rm = RoiManager()
	rm.reset()

	rm.addRoi(roi_1)
	rm.addRoi(roi_2)
	rm.addRoi(roi_3)
	rm.addRoi(roi_4)

	rm.select(0)
	rm.rename(0, "ROI FUS")
	rm.runCommand("Set Color", "yellow")

	rm.select(1)
	rm.rename(1, "ROI DNAJB6")
	rm.runCommand("Set Color", "blue")

	rm.select(2)
	rm.rename(2, "ROI DNAJB6 touching FUS")
	rm.runCommand("Set Color", "red")

	rm.select(3)
	rm.rename(3, "ROI FUS touching DNAJB6")
	rm.runCommand("Set Color", "green")

	rm.runCommand(imp1, "Show All")

	#Change distance to be in um
	cal = imp.getCalibration()
	min_distance = str(round((cal.pixelWidth * min_dist),1))

	table = ResultsTable()
	table.incrementCounter()
	table.addValue("Numbers of FUS Markers", roi_1.getCount(0))
	table.addValue("Numbers of DNAJB6 Markers", roi_2.getCount(0))
	table.addValue("Numbers of DNAJB6 within %s um of FUS" %(min_distance), roi_3.getCount(0))
	table.addValue("Numbers of FUS within %s um of DNAJB6" %(min_distance), roi_4.getCount(0))

	table.show("Results of Analysis")

run()
