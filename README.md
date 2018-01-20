# Image-Processor
Overlays logos and a banner onto input images

## Setup instructions
This script works with both python2 and python3.
Download zip file from [this link](https://github.com/jezgillen/Image-Processor/archive/mac.zip "Image Processor.zip"). 
Unzip file, to find the Image Processor script and three folders.
The images to be processed can be put in the 'input' folder, 
the banner image should be put in the 'top' folder, 
and the logos to be placed at the bottom of the input should go in the 'bottom' folder.
There are example images already in these folders to test the program on.

To install required packages, go to the unzipped folder in the terminal and run:
```sudo pip install -r requirements.txt```
If you don't have pip, you'll have to install that first

If this is successful, you can then run the script with:
```python imageProcessor.py```

