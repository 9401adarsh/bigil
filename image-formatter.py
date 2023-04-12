import cv2
from typing import *


def convertImgToYCbCr(imagePath: str) -> Tuple:
    
    img = cv2.imread(imagePath)
    # Convert the image to the YCbCr color space
    ycbcr_img = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)

    # Split the YCbCr image into its three color channels
    y_channel, cb_channel, cr_channel = cv2.split(ycbcr_img)
    
    print('Given Image has been broken down to three channels as per the YCbCr Color Space.')
    return (y_channel, cb_channel, cr_channel)



    