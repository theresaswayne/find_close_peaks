 ImageJ Python script to find intensity peaks in 2 different channels that are within a defined distance.  
==================================

Input images can be 2D or 3D. 
3D images will be projected. (Note: use projections with care; they can produce false colocalization.)

## Usage

Open the script in the ImageJ [Script Editor](https://imagej.net/Scripting)

Before running, experiment with your image to find the best values for:
- rolling ball background subtraction radius
- min and max puncta size in pixels
- typical peak height
- maximum distance in pixels that should be accepted as "colocalized"

## Single image version (find_close_peaks)

1. Run the script. It will prompt you to open an image. (Supports anything that Bio-Formats can open).
2. In the dialog, specify the parameters.
- Channels 1 and 2 are the channels to be analyzed. (In original script, #1 becomes Neuron and #2 becomes Glioma in results table) 
- radius background is used for rolling ball background subtraction – establish this first in the IJ command (pixel units) 
- sigma smaller and larger are the smallest and largest objects expected (pixel units) 
- min peak value is the height  
- min dist is the distance in pixels that counts as colocalized 
3. Output (displayed in IJ, not saved, but you can save if you want): 
- Summary table of results  
- Point ROIs representing the 2 classes of puncta, plus the “touching” (within distance criterion) puncta. The 2 “touching” ROIs are not always equivalent, e.g. if there are 2 closely spaced puncta in 1 channel that are both close to the same point in another. 
- Images of each relevant channel, projected (if applicable) and background subtracted

## Batch version (batch)
1. Run the script. It will prompt you for input and output directories.
2. Specify parameters as above.
3. Output will be saved for you.

## Credits

Original by Cedric Espenel, Stanford University

Modified by Theresa Swayne, Columbia University
