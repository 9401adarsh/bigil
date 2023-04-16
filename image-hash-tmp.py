from imagehash import ANTIALIAS, ImageHash, phash
from PIL import Image
import numpy as np
import cv2
import pywt
import math
from typing import *
import time


class processImage(): 
    
    def __init__(self, imagePath) -> None:
        self.imagePath = imagePath
        self.channels = {}
        self.waveletBands = {}
        self.coeffMatrix = {}
        self.reconstructedChannels = {}
        pass

    def imageToYCbCr(self) -> Tuple: 
        
        ##img = cv2.imread(self.imagePath)
        img = Image.open(self.imagePath)
		##Resizing image to nearest 2^k x 2^k - for SPIHT

        ##print('Image Width is', img.shape[1])
        ##print('Image Height is', img.shape[0])

        # Convert the image to the YCbCr color space
        ##('resizing to a size of 256 x 256 for starters: ')
        img = img.resize((128, 128)).convert('YCbCr')
        

        channelMatrix = img.split()

        # Split the YCbCr image into its three color channels
        y_channel, cb_channel, cr_channel = np.array(channelMatrix[0]), np.array(channelMatrix[1]), np.array(channelMatrix[2])
        ##print(y_channel)
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
            self.waveletBands[channelType] = self.waveletDecompose(self.channels[channelType])
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

        """

        currentSize = cA[i - 1].shape[0] * cA[i - 1].shape[1]
        cHi, cVi, cDi = coeffs[i]
        cA[i] = np.concatenate((cA[i - 1], cHi, cVi, cDi), axis = None).reshape(2 * currentSize, 2 * currentSize)

        """
        currentIdx = 1

        while currentIdx < len(coeffs): 
            i = currentIdx
            currentSize = cA[i - 1].shape[0]
            ##print(f'current size : {currentSize}')
            cHi, cVi, cDi = coeffs[i]

            subMat1 = np.concatenate((cA[i - 1], cHi), axis = 1)
            subMat2 = np.concatenate((cVi, cDi), axis = 1)
            cA.append(np.concatenate((subMat1, subMat2), axis = 0))

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
            ##print(coeffs[-1])
            currentMatrix = subMatrices[0]
            currLevel = currLevel - 1
        coeffs.append(currentMatrix)
        ##print(coeffs[-1].shape)
        coeffs.reverse()
        return coeffs
        
    def reconstructChannelFromCoeffs(self, coeffs): 
        return pywt.waverec2(coeffs, 'haar')
    
    def reconstructChannels(self, compressedWaveletChannels):
        for k, compressedWavelet in compressedWaveletChannels.items():
            self.reconstructedChannels[k] = pywt.waverec2(compressedWavelet['coeffs'], 'haar')
        return self.reconstructedChannels
##defined for images of 2^k * 2k size only for now

class SPIHT: 
    def __init__(self, channelMatrix):    
        self.channelMatrix = channelMatrix
        ##print(channelMatrix)
        ##print(channelMatrix.shape)
        self.lis = []
        self.lip = []
        self.lsp = []
        self.tmpLSP = []
        self.threshold = None
        self.encodedString = ''
        if self.channelMatrix is not None: 
            self.threshold = math.floor(math.log2(max(abs(channelMatrix).flatten())))

    def getSign(self, pixels): 
        i, j = pixels
        if self.channelMatrix[i][j] >= 0: 
            return '1'
        else:
            return '0'
    
    def isSignifigant(self, pixels, bitPlane: int) -> bool : 
        #print(pixels)
        pixelValues = [abs(self.channelMatrix[i][j]) for (i, j) in pixels]
        ##print(pixelValues)
        return max(pixelValues) >= (1 << bitPlane)
    
    def getKthSignificantBit(self, num, k): 
        bitStr = bin(num)[2:]
        for bit in bitStr: 
            if bit == '1': 
                k = k - 1
            if k == 0: 
                return '1'
        return '0'

    def initialize(self, decompLvls):
        shapeX, shapeY = self.channelMatrix.shape
        ##print(shapeX, shapeY)
        maxLimit = int(shapeX * shapeY / (1 << (2 * decompLvls)))
        ##print(maxLimit)
        for i in range(0, maxLimit + 1): 
            for j in range(0, maxLimit + 1): 
                self.lip.append((i, j))
                #print(self.lip)
                ##print(f'descendants of {(i, j)} are {self.getDescendants((i, j))}')
                if len(self.getDescendants((i, j))) != 0 and (i, j) != (0, 0): 
                    self.lis.append(('D', i, j))
        return

    def reset(self): 
        self.lis, self.lip, self.lsp, self.tmpLSP, self.encodedString = [], set(), set(), set(), ''
        return 
        
    def processLIP(self, bitPlane: int): 
        ##print(f'lip : {self.lip}')
        copyLIP = self.lip.copy()
        toRemove = []
        for (i, j) in copyLIP: 
            isSignificant = self.isSignifigant({(i, j)}, bitPlane)
            if isSignificant == True: 
                self.tmpLSP.append((i, j))
                toRemove.append((i, j))
                #self.encodedString += self.getSign((i, j))
                ##output sign of value at (i,j)
        for lip in toRemove: 
            self.lip.remove(lip)
        #print(f'lip : {self.lip}')
        return
    
    def getOffspring(self, srcPixels: tuple): 
        i, j = srcPixels
        offspring = []
        for pX in range(i << 1, (i << 1) + 2):
            for pY in range(j << 1, (j << 1) + 2): 
                if pX < self.channelMatrix.shape[0] and pY < self.channelMatrix.shape[1] and (pX, pY) != (i, j):
                    offspring.append((pX, pY))
        return offspring
    
    def getDescendants(self, srcPixels: tuple):
        i, j = srcPixels
        children = self.getOffspring((i, j))
        descendants = children 
        for child in children: 
            descendants = descendants + self.getDescendants(child)
        return descendants
    
    def processDSet(self, lisPixels, bitPlane): 
        ##print(f'processing D - Set for pixel - {lisPixels}')
        descendants = self.getDescendants(lisPixels)
        decrementIdx = False
        ##print(f'descendants for {lisPixels} : {descendants}')
        ##print(f'Signifigance of D{lisPixels} with threshold = {1 << bitPlane} - {self.isSignifigant(descendants, bitPlane)}')

        if self.isSignifigant(descendants, bitPlane) == True:
            ##print(f'offspring for {lisPixels} is {self.getOffspring(lisPixels)}')
            ##print(f'test offspring for {lisPixels}')
            for child in self.getOffspring(lisPixels):
                isChildSignificant = self.isSignifigant({child}, bitPlane)
                #self.encodedString += '1' if isChildSignificant else '0'
                ##output isChildSignifigant
                ##print(f'checking if {child} is signifigant')
                if isChildSignificant == True:
                    ##print(f'adding {child} to LSP')
                    self.tmpLSP.append(child)
                    ##self.encodedString += self.getSign(child)
                    ##output sign of coefficient of child 
                elif isChildSignificant == False: 
                    self.lip.append(child)
            offspring = self.getOffspring(lisPixels)
            descendantsWithoutChildren = descendants 
            for child in offspring: 
                try: 
                    descendantsWithoutChildren.remove(child)
                except:
                    pass
            ##print(f'L - set for {lisPixels} is \n : {descendantsWithoutChildren}')
            if len(descendantsWithoutChildren) != 0: 
                ##print(f'type change from D to L for {lisPixels}')
                if not ('L', *lisPixels) in self.lis: 
                    self.lis.append(('L', *lisPixels))
                ##self.processLSet(lisPixels, bitPlane)
            ##print(f'removing D-set {lisPixels}')
            self.lis.remove(('D', *lisPixels))
            decrementIdx = True
            ##print(self.lis)
        return decrementIdx
    
    def processLSet(self, lisPixels, bitPlane):
        ##print(f'processing L - Set for pixel - {lisPixels}')
        offspring = self.getOffspring(lisPixels)
        descendantsWithoutChildren = self.getDescendants(lisPixels)
        for child in offspring: 
            try: 
                descendantsWithoutChildren.remove(child)
            except:
                pass
        isSignifigant = self.isSignifigant(descendantsWithoutChildren, bitPlane)
        decrementFlag = False
        ##self.encodedString += '1' if isSignifigant else '0'
        ##output isSignifigant
        if isSignifigant == True: 
            offspring = self.getOffspring(lisPixels)
            ##print(f'offspring for {lisPixels} is {offspring}')
            for child in offspring: 
                if ('D', *child) not in self.lis: 
                    ##print(f'appending D, {child}')
                    self.lis.append(('D', *child))
            self.lis.remove(('L', *lisPixels))
            ##print(self.lis)
            decrementFlag = True
        ##print(self.lis)
        return decrementFlag
    
    def processLIS(self, bitPlane: int): 
        ##copyLIS = self.lis.copy()
        currentIdx = 0
        while currentIdx < len(self.lis):
            (setType, i, j) = self.lis[currentIdx]
            ##print(f'processing Set for pixel - {(setType, i, j)}')
            if setType == 'D': 
                flag = self.processDSet((i, j), bitPlane)
                currentIdx = currentIdx - 1 if flag else currentIdx
            elif setType == 'L': 
                flag = self.processLSet((i, j), bitPlane)
                currentIdx = currentIdx - 1 if flag else currentIdx
            currentIdx += 1

    """         for (setType, i, j) in self.lis: 
            ##print(f'LIS in this pass : {self.lis}')
            print(f'processing Set for pixel - {(setType, i, j)}')
            if setType == 'D': 
                self.processDSet((i, j), bitPlane)
            elif setType == 'L': 
                self.processLSet((i, j), bitPlane) """
    
    def sortingPass(self, bitPlane): 
        ##print('processing LIP.')
        self.processLIP(bitPlane)
        ##print('processed LIP. processing LIS')
        self.processLIS(bitPlane)
        ##print('processed LIS. moving to refinement')
        ##print(f'lsp : {self.lsp} , lis : {self.lis}, lip : {self.lip}, tmpLSP : {self.tmpLSP}')
        ##print('moving to refinement stage')

    def processLSP(self, bitPlane): 
        for sigPixels in self.lsp: 
            i, j = sigPixels
            intensity = abs(self.channelMatrix[i][j])
            #output nth most signifigant bit of intensity
            #self.encodedString += self.getKthSignificantBit(intensity, bitPlane)
            continue
        ##print(self.lsp)
        self.lsp = self.lsp + self.tmpLSP
        self.tmpLSP = []
        return
    
    def refinementPass(self, bitPlane):
        self.processLSP(bitPlane)
        #print('refinement done, updating threshold to threshold / 2')
        return

    def encodeSPIHT(self, decompLevels, numPasses = 3): 
        ##self.reset()
        self.initialize(decompLevels)

        bitPlane = self.threshold

        ##print(f'threshold is {self.threshold}')
        ##print(f'{self.lip}')

        while numPasses > 0: 
            
            self.sortingPass(bitPlane)
            self.refinementPass(bitPlane)
            bitPlane -= 1
            numPasses -= 1

        ##print(f'stopping theshold is {1 << bitPlane}')
        ##print(f'output is {self.encodedString}')
        return {'lis': self.lis, 'lsp' : self.lsp, 'lip' : self.lip, 'encodedStr' : self.encodedString}
    
    def compress(self, lsp = None): 
        compressedChannelMatrix = np.zeros(self.channelMatrix.shape)
        for i, j in lsp: 
            compressedChannelMatrix[i][j] = self.channelMatrix[i][j]
        return compressedChannelMatrix
    

def compressImage(imagePath):
    processImageObj = processImage(imagePath)
    processImageObj.initializeInputForSPIHT()
    
    spihtObj = {}
    spihtResult = {}
    compressedWaveletChannels = {}

    for k, waveletChannelMatrix in processImageObj.coeffMatrix.items():
        spihtObj[k] = SPIHT(waveletChannelMatrix)
        lvls = processImageObj.waveletBands[k][1]
        ##start_time = time.time()
        spihtResult[k] = spihtObj[k].encodeSPIHT(decompLevels = lvls, numPasses= 7)
        ##print("--- %s seconds ---" % (time.time() - start_time))
        lsp = spihtResult[k]['lsp']
        compressedWaveletChannelMatrix = spihtObj[k].compress(lsp)
        compressedWaveletChannels[k] = {'matrix': compressedWaveletChannelMatrix, 'coeffs' : processImageObj.matrixTocoeffs(compressedWaveletChannelMatrix, lvls)}
    
    reconstructedChannels = processImageObj.reconstructChannels(compressedWaveletChannels)
    
	#print(reconstructedChannels['cB'].astype('uint8'))
    #print(reconstructedChannels['cB'].astype('uint8').shape)
    finalCompressedChannelMatrix = [Image.fromarray(reconstructedChannels['y'].astype('uint8')), Image.fromarray(reconstructedChannels['cB'].astype('uint8')), Image.fromarray(reconstructedChannels['cR'].astype('uint8'))]
    compressedImageMatrix = Image.merge('YCbCr', finalCompressedChannelMatrix)

    return compressedImageMatrix ##returns Image Object

def saveCompressedImage(imageObj, filePath = './lena-compress.jpg'):
    imageObj.save(filePath)






def whash(image, hash_size=8, image_scale=None, mode='haar', remove_max_haar_ll=True):
	"""
	Wavelet Hash computation.

	based on https://www.kaggle.com/c/avito-duplicate-ads-detection/

	@image must be a PIL instance.
	@hash_size must be a power of 2 and less than @image_scale.
	@image_scale must be power of 2 and less than image size. By default is equal to max
					power of 2 for an input image.
	@mode (see modes in pywt library):
					'haar' - Haar wavelets, by default
					'db4' - Daubechies wavelets
	@remove_max_haar_ll - remove the lowest low level (LL) frequency using Haar wavelet.
	"""
	import pywt
	if image_scale is not None:
		assert image_scale & (image_scale - 1) == 0, 'image_scale is not power of 2'
	else:
		image_natural_scale = 2**int(np.log2(min(image.size)))
		image_scale = max(image_natural_scale, hash_size)

	ll_max_level = int(np.log2(image_scale))

	level = int(np.log2(hash_size))
	assert hash_size & (hash_size - 1) == 0, 'hash_size is not power of 2'
	assert level <= ll_max_level, 'hash_size in a wrong range'
	dwt_level = ll_max_level - level

	image = image.convert('L').resize((image_scale, image_scale), ANTIALIAS)
	pixels = np.asarray(image) / 255

	# Remove low level frequency LL(max_ll) if @remove_max_haar_ll using haar filter
	if remove_max_haar_ll:
		coeffs = pywt.wavedec2(pixels, 'haar', level=ll_max_level)
		coeffs = list(coeffs)
		coeffs[0] *= 0
		pixels = pywt.waverec2(coeffs, 'haar')

	# Use LL(K) as freq, where K is log2(@hash_size)
	coeffs = pywt.wavedec2(pixels, mode, level=dwt_level)
	dwt_low = coeffs[0]

	# Substract median and compute hash
	med = np.median(dwt_low)
	diff = dwt_low > med
	return ImageHash(diff)

start_time = time.time()
resultOG = compressImage('./ex-3-og.jpeg')
print("--- %s seconds ---" % (time.time() - start_time))
saveCompressedImage(resultOG, './ex-3-og-comp.jpeg')

start_time = time.time()
hashResultOG = phash(resultOG)
print("--- %s seconds ---" % (time.time() - start_time))
print(hashResultOG)

start_time = time.time()
resultEdit = compressImage('./ex-3-edit.jpeg')
print("--- %s seconds ---" % (time.time() - start_time))
saveCompressedImage(resultEdit, './ex-3-edit-comp.jpeg')

start_time = time.time()
hashResultEdit = phash(resultEdit, hash_size=16)
print("--- %s seconds ---" % (time.time() - start_time))
print(hashResultEdit)


start_time = time.time()
resultLena = compressImage('./lena_color.jpeg')
print("--- %s seconds ---" % (time.time() - start_time))
saveCompressedImage(resultLena, './lena-color-comp.jpeg')




whiteImg = Image.open('./ex-3-og-comp.jpeg').resize((128, 128))
blackImg = Image.open('./ex-3-edit-comp.jpeg').resize((128, 128))

#print(f'hamming distance: {phash(resultLena, hash_size=16) - hashResultEdit}')
##print(f'hamming distance: {whash(whiteImg) - whash(blackImg)}')
print(f'hamming distance: {phash(whiteImg, hash_size=8) - phash(blackImg, hash_size=8)}')
print(f'hamming distance: {whash(whiteImg, hash_size=8) - whash(blackImg, hash_size=8)}')