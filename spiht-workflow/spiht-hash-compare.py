from PIL import Image
from imagehash import whash, ImageHash
import numpy as np
from typing import *
from typing import *
import SPIHT
import processImage


def compressImageUsingSPIHT(image: Image.Image):
    imageProcessor = processImage(image)
    imageProcessor.initializeInputForSPIHT()
    spihtObj = {}
    spihtResult = {}
    compressedWaveletChannels = {}
    for k, waveletChannelMatrix in imageProcessor.coeffMatrix.items():
        spihtObj[k] = SPIHT(waveletChannelMatrix)
        lvls = imageProcessor.waveletBands[k][1]
        ##start_time = time.time()
        spihtResult[k] = spihtObj[k].encodeSPIHT(decompLevels = lvls, numPasses= 7)
        ##print("--- %s seconds ---" % (time.time() - start_time))
        lsp = spihtResult[k]['lsp']
        compressedWaveletChannelMatrix = spihtObj[k].compress(lsp)
        compressedWaveletChannels[k] = {'matrix': compressedWaveletChannelMatrix, 'coeffs' : imageProcessor.matrixTocoeffs(compressedWaveletChannelMatrix, lvls)}
    reconstructedChannels = imageProcessor.reconstructChannels(compressedWaveletChannels)
	#print(reconstructedChannels['cB'].astype('uint8'))
    #print(reconstructedChannels['cB'].astype('uint8').shape)
    finalCompressedChannelMatrix = [Image.fromarray(reconstructedChannels['y'].astype('uint8')), Image.fromarray(reconstructedChannels['cB'].astype('uint8')), Image.fromarray(reconstructedChannels['cR'].astype('uint8'))]
    compressedImage = Image.merge('YCbCr', finalCompressedChannelMatrix)
    return compressedImage ##returns Image Object

def computeWHash(image: Image.Image) -> ImageHash :
    return whash(image, hash_size=8)

def compareWHashes(image1 : Image.Image, image2 : Image.Image2) -> ImageHash: 
    return computeWHash(image1) - computeWHash(image2)

def compareAgainstImagesInCloud(newImage: Image.Image) -> Tuple(Image.Image, int) | int:
    compressedNewImage = compressImageUsingSPIHT(newImage)
    candidateImageHDTuple = None ## Tiple => (Image.Image, int)
    cloudImages = [] ##retrieveImagesFromCloud()
    for cloudImage in cloudImages: 
        compressedCloudImage = compressImageUsingSPIHT(cloudImage)
        hammingDistance = compareWHashes(compressedNewImage, compressedCloudImage)
        candidateImageHDTuple = (cloudImage, hammingDistance) if candidateImageHDTuple is None else (cloudImage, min(hammingDistance, candidateImageHDTuple[1]))
    return candidateImageHDTuple if candidateImageHDTuple is not None else -2e20