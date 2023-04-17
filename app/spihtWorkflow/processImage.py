from PIL import Image
import numpy as np
import pywt
from typing import *

# resizes images to 128 x 128 for the purpose of SPIHT comparison


class processImage():

    def __init__(self, image=None) -> None:
        self.image = image.resize((128, 128))
        self.channels = {}
        self.waveletBands = {}
        self.coeffMatrix = {}
        self.reconstructedChannels = {}
        pass

    def imageToYCbCr(self) -> Tuple:
        self.image = self.image.convert('YCbCr')
        channelMatrix = self.image.split()
        # Split the YCbCr image into its three color channels
        y_channel, cb_channel, cr_channel = np.array(channelMatrix[0]), np.array(
            channelMatrix[1]), np.array(channelMatrix[2])
        # print(y_channel)
        ##print('Given Image has been broken down to three channels as per the YCbCr Color Space.')
        self.channels['y'] = y_channel
        self.channels['cB'] = cb_channel
        self.channels['cR'] = cr_channel
        return (y_channel, cb_channel, cr_channel)

    def waveletDecompose(self, channel):
        coeffs = pywt.wavedec2(channel, 'haar')
        return (coeffs, len(coeffs) - 1)

    def imageWaveletDecompose(self):
        if self.channels == {}:
            return None
        for channelType in ['y', 'cB', 'cR']:
            self.waveletBands[channelType] = self.waveletDecompose(
                self.channels[channelType])
        return self.waveletBands

    def initializeInputForSPIHT(self):
        self.imageToYCbCr()
        self.imageWaveletDecompose()
        ##print('Image has been resized, if need be to 256 x 256 for now')
        for k, (coeffs, lvls) in self.waveletBands.items():
            self.coeffMatrix[k] = self.coeffsToArray(coeffs)
        return self.coeffMatrix

    def coeffsToArray(self, coeffs):
        cA = []
        cA.append(coeffs[0])
        currentIdx = 1
        while currentIdx < len(coeffs):
            i = currentIdx
            ##print(f'current size : {currentSize}')
            cHi, cVi, cDi = coeffs[i]
            subMat1 = np.concatenate((cA[i - 1], cHi), axis=1)
            subMat2 = np.concatenate((cVi, cDi), axis=1)
            cA.append(np.concatenate((subMat1, subMat2), axis=0))
            currentIdx = currentIdx + 1

        return cA[-1]

    def split(self, squareMatrix):
        r, h = squareMatrix.shape
        nrows, ncols = r // 2, h // 2
        return (squareMatrix.reshape(h//nrows, nrows, -1, ncols)
                .swapaxes(1, 2)
                .reshape(-1, nrows, ncols))

    def matrixTocoeffs(self, matrix, levels):
        coeffs = []
        currentMatrix = matrix.copy()
        currLevel = levels
        while currLevel > 0:
            subMatrices = self.split(currentMatrix)
            (cHi, cVi, cDi) = subMatrices[1], subMatrices[2], subMatrices[3]
            coeffs.append((cHi, cVi, cDi))
            # print(coeffs[-1])
            currentMatrix = subMatrices[0]
            currLevel = currLevel - 1
        coeffs.append(currentMatrix)
        # print(coeffs[-1].shape)
        coeffs.reverse()
        return coeffs

    def reconstructChannelFromCoeffs(self, coeffs):
        return pywt.waverec2(coeffs, 'haar')

    def reconstructChannels(self, compressedWaveletChannels):
        for k, compressedWavelet in compressedWaveletChannels.items():
            self.reconstructedChannels[k] = pywt.waverec2(
                compressedWavelet['coeffs'], 'haar')
        return self.reconstructedChannels
