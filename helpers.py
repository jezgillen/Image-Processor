import os
import sys
import cv2
import numpy as np
DEBUG = False

def overlay_transparent(background_img, img_to_overlay_t, x, y, shadow=False):
    """
    @brief      Overlays a transparant PNG onto another image using CV2
    
    @param      background_img    The background image
    @param      img_to_overlay_t  The transparent image to overlay (has alpha channel)
    @param      x                 x location to place the top-left corner of our overlay
    @param      y                 y location to place the top-left corner of our overlay
    
    @return     Background image with overlay on top
    """


    if DEBUG:
        print('background shape: ', background_img.shape)
        print('overlay shape: ', img_to_overlay_t.shape)
        print('x and y position of image to be placed: ', x,y)
    
    assert 0 <= x <= background_img.shape[1] - img_to_overlay_t.shape[1], \
                        "attempting to place image in impossible position"
    assert 0 <= y <= background_img.shape[0] - img_to_overlay_t.shape[0], \
                        "attempting to place image in impossible position"
    x = int(x)
    y = int(y)

    bg_img = background_img
    h, w, d = img_to_overlay_t.shape

    if(d == 3):
        bg_img[y:y+h, x:x+w] = img_to_overlay_t
        return bg_img
        
    
    # Extract the alpha mask of the RGBA image, convert to RGB 
    b,g,r,mask = cv2.split(img_to_overlay_t)
    overlay_color = cv2.merge((b,g,r))


    background_area_of_interest = bg_img[y:y+h, x:x+w]

    #turn mask into 3 channels
    temp = np.zeros_like(overlay_color)
    temp[:,:,0] = mask
    temp[:,:,1] = mask
    temp[:,:,2] = mask
    mask = temp

    # Fade out the logo from the background image.
    img1_bg = cv2.multiply(cv2.bitwise_not(mask), background_area_of_interest, scale=1./255)

    # Fade out the logo from the logo image in prep for addition.
    img2_fg = cv2.multiply(mask, overlay_color, scale=1./255)

    # Update the original image with our new ROI
    bg_img[y:y+h, x:x+w] = cv2.add(img1_bg, img2_fg)
    return bg_img

def resize_to_fraction(bot,background_shape,fraction=0.2):
    height = background_shape[0] * fraction
    ratio = height/bot.shape[0]
    bot = cv2.resize(bot,(0,0),fx=ratio,fy=ratio,interpolation=cv2.INTER_AREA)
    return bot

def resize_banner_to_fit_background(img,background_shape):
    length = background_shape[1]
    ratio = length/img.shape[1]
    img = cv2.resize(img,(0,0),fx=ratio,fy=ratio,interpolation=cv2.INTER_AREA)
    return img

def find_top_and_bottom_of_object(image):
    img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    reference = np.sum(img[0,:])
    for i, row in enumerate(img):
        if(np.sum(row) != reference):
            top_of_obj = i
            break

    reference = np.sum(img[-1,:])
    for i in range(img.shape[0]-1,0,-1):
        if(np.sum(img[i,:]) != reference):
            bottom_of_obj = i
            break

    return top_of_obj-1, bottom_of_obj+2
