from PIL import Image
import os
from imagehash import whash, ImageHash
import numpy as np
from typing import *
from typing import *
from spihtWorkflow.spiht import SPIHT
from spihtWorkflow.processImage import processImage


def compressImageUsingSPIHT(image: Image.Image):
    imageProcessor = processImage(image)
    imageProcessor.initializeInputForSPIHT()
    spihtObj = {}
    spihtResult = {}
    compressedWaveletChannels = {}
    for k, waveletChannelMatrix in imageProcessor.coeffMatrix.items():
        spihtObj[k] = SPIHT(waveletChannelMatrix)
        lvls = imageProcessor.waveletBands[k][1]
        # start_time = time.time()
        spihtResult[k] = spihtObj[k].encodeSPIHT(
            decompLevels=lvls, numPasses=7)
        # print("--- %s seconds ---" % (time.time() - start_time))
        lsp = spihtResult[k]['lsp']
        compressedWaveletChannelMatrix = spihtObj[k].compress(lsp)
        compressedWaveletChannels[k] = {'matrix': compressedWaveletChannelMatrix,
                                        'coeffs': imageProcessor.matrixTocoeffs(compressedWaveletChannelMatrix, lvls)}
    reconstructedChannels = imageProcessor.reconstructChannels(
        compressedWaveletChannels)
    # print(reconstructedChannels['cB'].astype('uint8'))
    # print(reconstructedChannels['cB'].astype('uint8').shape)
    finalCompressedChannelMatrix = [Image.fromarray(reconstructedChannels['y'].astype('uint8')), Image.fromarray(
        reconstructedChannels['cB'].astype('uint8')), Image.fromarray(reconstructedChannels['cR'].astype('uint8'))]
    compressedImage = Image.merge('YCbCr', finalCompressedChannelMatrix)
    return compressedImage  # returns Image Object


def computeWHash(image: Image.Image) -> ImageHash:
    return whash(image, hash_size=8)


def compareWHashes(image1: Image.Image, image2: Image.Image) -> ImageHash:
    return computeWHash(image1) - computeWHash(image2)


def compareAgainstImagesInCloud(newImage: Image.Image):
    compressedNewImage = compressImageUsingSPIHT(newImage)
    candidateImageHDTuple = None  # Tiple => (Image.Image, int)
    cloudImages = []
    # fetch all files from dataStorage folder
    for filename in os.listdir('./dataStorage'):
        if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.jpeg'):
            # open the image file and add its data to the list
            image = Image.open('./dataStorage/' + filename)
            cloudImages.append(image)  # retrieveImagesFromCloud()
    for cloudImage in cloudImages:
        compressedCloudImage = compressImageUsingSPIHT(cloudImage)
        hammingDistance = compareWHashes(
            compressedNewImage, compressedCloudImage)
        print(cloudImage.filename, hammingDistance)
        if candidateImageHDTuple is None:
            candidateImageHDTuple = (cloudImage, hammingDistance)
        else:
            if hammingDistance < candidateImageHDTuple[1]:
                candidateImageHDTuple = (cloudImage, hammingDistance)
    return candidateImageHDTuple if candidateImageHDTuple is not None else -2e20
