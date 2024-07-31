# ROI_to_mask_single.py
# Given an ROI in the manager, and a multichannel single-slice image, measure the mask area, create a mask and save the data and mask
# Image must be open

# ---- Import packages

from ij import IJ, ImagePlus, ImageStack
from ij.plugin.filter import RankFilters
import net.imagej.ops
from net.imglib2.view import Views
from net.imglib2.img.display.imagej import ImageJFunctions as IL
from ij.gui import Roi, PointRoi
from jarray import zeros
from ij.measure import ResultsTable
from math import sqrt
from java.awt import Color
from ij.plugin.frame import RoiManager
from ij.gui import GenericDialog

# ---- Define functions

# def -- 

def run():

	# setup: clear ROI Mgr
	rm = RoiManager.getInstance()
	if not rm:
	  rm = RoiManager()
	rm.reset()

	# obtain an image
	imp = IJ.openImage("http://imagej.net/images/blobs.gif");

	# create an ROI and add to manager
	imp.setRoi(108,33,70,117);
	roi = imp.getRoi()
	rm.addRoi(roi);

	# create the mask and show it
	mask = imp.createRoiMask()
	maskImp = ImagePlus("Mask", mask)
	maskImp.show()
	
	# change values from 0,255 to 0,1 and display in a good LUT
	IJ.run(maskImp, "Divide...", "value=255");
	IJ.run(maskImp, "glasbey_inverted", "display=Mask")
	
	IJ.log("Done")

# ---- Run
run()