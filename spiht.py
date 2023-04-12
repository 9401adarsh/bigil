import cv2
import pywt
import numpy as np

class SPIHT:
    def __init__(self, k=5):
        self.k = k
        self.y_wavelet = None
        self.cb_wavelet = None
        self.cr_wavelet = None
        self.y_significant = []
        self.cb_significant = []
        self.cr_significant = []
        
    def _sort_and_threshold(self, subband):
        print(f'Inside sort and threshold helper -> \n {subband}')
        sorted_coefficients = sorted(abs(subband).flatten(), reverse=True)
        threshold = sorted_coefficients[self.k-1]
        significant_coefficients = []
        for coefficient in subband.flatten():
            if abs(coefficient) >= threshold:
                significant_coefficients.append(coefficient)
            else:
                significant_coefficients.append(0)
        print(len(significant_coefficients))
        print(significant_coefficients)
        return significant_coefficients
    
    def compress(self, img_path):
        # Load the input image and convert it to the YCbCr color space
        original_img = cv2.imread(img_path)
        ycbcr_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2YCR_CB)
        ycbcr_channels = cv2.split(ycbcr_img)
        
        print(ycbcr_channels)

        # Perform the forward wavelet transform on each color channel
        self.y_wavelet = pywt.dwt2(ycbcr_channels[0], 'haar')
        self.cb_wavelet = pywt.dwt2(ycbcr_channels[1], 'haar')
        self.cr_wavelet = pywt.dwt2(ycbcr_channels[2], 'haar')
        
        # Process each subband separately
        for wavelet, significant in [(self.y_wavelet, self.y_significant),
                                     (self.cb_wavelet, self.cb_significant),
                                     (self.cr_wavelet, self.cr_significant)]:
            subbands = []
            cA, (cH, cV, cD) = wavelet
            for wavelet in [cA, cH, cV, cD]:
                subbands.append(wavelet)
            for subband in subbands:
                significant.extend(self._sort_and_threshold(subband))
            
            ##print(significant)

        print(type(self.y_significant))
        print(len(self.y_significant))
        # Perform the inverse wavelet transform on each color channel using the significant coefficients
        y_reconstructed = pywt.idwt2(self.y_significant, 'haar')
        cb_reconstructed = pywt.idwt2(self.cb_significant, 'haar')
        cr_reconstructed = pywt.idwt2(self.cr_significant, 'haar')
        
        # Merge the three color channels back into a single color image
        ycbcr_reconstructed = cv2.merge((y_reconstructed, cb_reconstructed, cr_reconstructed))
        
        # Convert the reconstructed image back to the BGR color space
        reconstructed_img = cv2.cvtColor(ycbcr_reconstructed, cv2.COLOR_YCR_CB2BGR)
        
        return reconstructed_img

SPIHTSolver = SPIHT()
SPIHTSolver.compress('./lena.jpg')