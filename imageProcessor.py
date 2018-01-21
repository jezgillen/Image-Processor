import os
import sys
import cv2
import numpy as np
from helpers import *

INPUT_DIR = "input"
TOP_DIR = "top"
BOTTOM_DIR = "bottom"
OUTPUT_DIR = "output"
DEBUG = False
BOT_RATIO = 0.4
BANNER_RATIO = 0.2
BUF = 500
OVERLAP = 30


if '-h' in sys.argv:
    print(
    '''
    Images should be in BMP, JPEG, PNG or TIFF format, using multiple formats at the same time is okay.
    A single banner image should be in a folder called 'top', if there are multiple, the first in alphebetical order will be chosen
    All images to be put at the bottom of the main image should be in a folder called 'bottom'. They will be placed on the image in alphebetical order
    All images to be processed should be in a folder called 'input'
    Processed images will be output in a folder called 'output', which you don't have to create
    
    Manual Mode

    The flag '-m' will start manual mode, which will allow you to set the size of the bottom images,
    and the vertical offset

    '''
    )
    exit()
elif('-m' in sys.argv):
    BOT_RATIO = input("Enter the vertical size of the bottom images as a fraction of the size of the input image (default is 0.4):\n")
    if not BOT_RATIO:
        BOT_RATIO = 0.4
    OVERLAP = input("Enter the vertical offset, the number of pixels to shift the input image down (default is 30):\n")
    if not OVERLAP:
        OVERLAP = 30
    BOT_RATIO = float(BOT_RATIO)
    BANNER_RATIO = float(BANNER_RATIO)
    OVERLAP = int(OVERLAP)
else:
    print("\n\tUse command: '%s -h' for help\n" % sys.argv[0])
    print("\n\tUse command: '%s -m' to manually set image locations\n" % sys.argv[0])

try:
    input_files = os.listdir(os.path.join(os.getcwd(),INPUT_DIR))
    top_files = sorted(os.listdir(os.path.join(os.getcwd(),TOP_DIR)))
    bottom_files = sorted(os.listdir(os.path.join(os.getcwd(),BOTTOM_DIR)))
except:
    print("One of '%s', '%s' or '%s' folders is not present" % (INPUT_DIR,TOP_DIR,BOTTOM_DIR))
    input("Press any key to exit")
    exit()

print("Top images: \n", top_files)
print("Bottom images: \n", bottom_files)

inputs = []
names = []
for img, name in zip([cv2.imread(os.path.join(INPUT_DIR,x)) for x in input_files], input_files):
    if(img is not None):
        inputs += [img]
        names += [name]

bottoms= [img for img in [cv2.imread(os.path.join(BOTTOM_DIR,x),-1) for x in bottom_files] if img is not None]
tops = [img for img in [cv2.imread(os.path.join(TOP_DIR,x),-1) for x in top_files] if img is not None]
input_files = names
print("Input images: \n", input_files)
print()

assert len(inputs) > 0, "No input images could be read"
assert len(bottoms) > 0, "No bottom images could be read"
assert len(tops) > 0, "No top images could be read"

for img, name in zip(inputs,input_files):
    #measure the vertical size of the object in the image
    top_of_obj, bottom_of_obj = find_top_and_bottom_of_object(img)
    distance_from_bottom =  bottom_of_obj - img.shape[0]

    #find final shape
    final_square_size = bottom_of_obj - top_of_obj + img.shape[0]*BANNER_RATIO + img.shape[0] * BOT_RATIO

    #resize bottoms to a fraction of image size
    new_bottoms = [resize_to_fraction(x,background_shape=img.shape,fraction=BOT_RATIO) for x in bottoms]

    #gap between bottom images
    gap_between_images = (final_square_size - sum([x.shape[1] for x in new_bottoms]))/(len(new_bottoms)+1)

    #add buffer to edges of img
    orig_img_shape = img.shape
    img = img[top_of_obj:bottom_of_obj,:,:]
    img = cv2.copyMakeBorder(img,
                             int(orig_img_shape[0]*BANNER_RATIO+OVERLAP),
                             int(orig_img_shape[0]*BOT_RATIO-OVERLAP),
                             int((final_square_size-img.shape[1])/2)+BUF,
                             int((final_square_size-img.shape[1])/2)+BUF,
                             cv2.BORDER_REPLICATE)

    for i in range(len(new_bottoms)):
        x_pos = (i+1)*int(gap_between_images) + sum([x.shape[1] for x in new_bottoms[:i]]) + BUF
        y_pos = img.shape[0]-new_bottoms[i].shape[0]
        img = overlay_transparent(img, new_bottoms[i], x_pos, y_pos)
    
    #top is a banner
    banner = tops[0]
    banner = resize_banner_to_fit_background(banner,background_shape=(final_square_size,final_square_size)) 
    img = overlay_transparent(img, banner, BUF, 0, shadow=True)

    #crop image to square
    img = img[:,BUF:img.shape[1]-BUF]
    
    #Save image 
    if(OUTPUT_DIR and not os.path.isdir(OUTPUT_DIR)):
        os.mkdir(OUTPUT_DIR)
    name = os.path.join(OUTPUT_DIR,name)
    try:
        os.remove(name)
    except:
        pass
    cv2.imwrite(name,img)
    print("Image '%s' has been created" % name)
