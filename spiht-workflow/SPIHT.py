from PIL import Image
import numpy as np
import math
from typing import *


class SPIHT: 
    def __init__(self, channelMatrix):    
        self.channelMatrix = channelMatrix
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
        pixelValues = [abs(self.channelMatrix[i][j]) for (i, j) in pixels]
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
        maxLimit = int(shapeX * shapeY / (1 << (2 * decompLvls)))
        for i in range(0, maxLimit + 1): 
            for j in range(0, maxLimit + 1): 
                self.lip.append((i, j))
                if len(self.getDescendants((i, j))) != 0 and (i, j) != (0, 0): 
                    self.lis.append(('D', i, j))
        return

    def reset(self): 
        self.lis, self.lip, self.lsp, self.tmpLSP, self.encodedString = [], set(), set(), set(), ''
        return 
        
    def processLIP(self, bitPlane: int): 
        copyLIP = self.lip.copy()
        toRemove = []
        for (i, j) in copyLIP: 
            isSignificant = self.isSignifigant({(i, j)}, bitPlane)
            if isSignificant == True: 
                self.tmpLSP.append((i, j))
                toRemove.append((i, j))
        for lip in toRemove: 
            self.lip.remove(lip)
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
        
        descendants = self.getDescendants(lisPixels)
        decrementIdx = False


        if self.isSignifigant(descendants, bitPlane) == True:

            for child in self.getOffspring(lisPixels):
                isChildSignificant = self.isSignifigant({child}, bitPlane)
                if isChildSignificant == True:
                    self.tmpLSP.append(child)
                elif isChildSignificant == False: 
                    self.lip.append(child)
            offspring = self.getOffspring(lisPixels)
            descendantsWithoutChildren = descendants 
            for child in offspring: 
                try: 
                    descendantsWithoutChildren.remove(child)
                except:
                    pass
            if len(descendantsWithoutChildren) != 0: 
                if not ('L', *lisPixels) in self.lis: 
                    self.lis.append(('L', *lisPixels))
            self.lis.remove(('D', *lisPixels))
            decrementIdx = True
        return decrementIdx
    
    def processLSet(self, lisPixels, bitPlane):
        offspring = self.getOffspring(lisPixels)
        descendantsWithoutChildren = self.getDescendants(lisPixels)
        for child in offspring: 
            try: 
                descendantsWithoutChildren.remove(child)
            except:
                pass
        isSignifigant = self.isSignifigant(descendantsWithoutChildren, bitPlane)
        decrementFlag = False
        if isSignifigant == True: 
            offspring = self.getOffspring(lisPixels)
            for child in offspring: 
                if ('D', *child) not in self.lis: 
                    self.lis.append(('D', *child))
            self.lis.remove(('L', *lisPixels))
            decrementFlag = True
        return decrementFlag
    
    def processLIS(self, bitPlane: int): 
        currentIdx = 0
        while currentIdx < len(self.lis):
            (setType, i, j) = self.lis[currentIdx]
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
        self.processLIP(bitPlane)
        self.processLIS(bitPlane)

    def processLSP(self, bitPlane): 
        """         
            for sigPixels in self.lsp: 
            i, j = sigPixels
            continue 
        """
        self.lsp = self.lsp + self.tmpLSP
        self.tmpLSP = []
        return
    
    def refinementPass(self, bitPlane):
        self.processLSP(bitPlane)
        return

    def encodeSPIHT(self, decompLevels, numPasses = 3): 
        self.initialize(decompLevels)
        bitPlane = self.threshold
        while numPasses > 0: 
            self.sortingPass(bitPlane)
            self.refinementPass(bitPlane)
            bitPlane -= 1
            numPasses -= 1
        return {'lis': self.lis, 'lsp' : self.lsp, 'lip' : self.lip, 'encodedStr' : self.encodedString}
    
    def compress(self, lsp = None): 
        compressedChannelMatrix = np.zeros(self.channelMatrix.shape)
        for i, j in lsp: 
            compressedChannelMatrix[i][j] = self.channelMatrix[i][j]
        return compressedChannelMatrix
    
