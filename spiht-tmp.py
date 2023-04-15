from typing import *
import numpy as np
import math


##defined for images of 2^k * 2k size only for now

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
        #print(pixels)
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

    def initialize(self, decompLvls = 2):
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
        for (i, j) in self.lip: 
            isSignificant = self.isSignifigant({(i, j)}, bitPlane)
            if isSignificant == True: 
                self.tmpLSP.append((i, j))
                self.lip.remove((i, j))
                self.encodedString += self.getSign((i, j))
                ##output sign of value at (i,j)
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
                self.encodedString += '1' if isChildSignificant else '0'
                ##output isChildSignifigant
                ##print(f'checking if {child} is signifigant')
                if isChildSignificant == True:
                    ##print(f'adding {child} to LSP')
                    self.tmpLSP.append(child)
                    self.encodedString += self.getSign(child)
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
            print(self.lis)
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
        self.encodedString += '1' if isSignifigant else '0'
        ##output isSignifigant
        if isSignifigant == True: 
            offspring = self.getOffspring(lisPixels)
            print(f'offspring for {lisPixels} is {offspring}')
            for child in offspring: 
                if ('D', *child) not in self.lis: 
                    print(f'appending D, {child}')
                    self.lis.append(('D', *child))
            self.lis.remove(('L', *lisPixels))
            print(self.lis)
            decrementFlag = True
        ##print(self.lis)
        return decrementFlag
    
    def processLIS(self, bitPlane: int): 
        ##copyLIS = self.lis.copy()
        currentIdx = 0
        while currentIdx < len(self.lis):
            (setType, i, j) = self.lis[currentIdx]
            print(f'processing Set for pixel - {(setType, i, j)}')
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
        print(f'lsp : {self.lsp} , lis : {self.lis}, lip : {self.lip}, tmpLSP : {self.tmpLSP}')
        print('moving to refinement stage')

    def processLSP(self, bitPlane): 
        for sigPixels in self.lsp: 
            i, j = sigPixels
            intensity = abs(self.channelMatrix[i][j])
            #output nth most signifigant bit of intensity
            self.encodedString += self.getKthSignificantBit(intensity, bitPlane)
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

        print(f'threshold is {self.threshold}')
        print(f'{self.lip}')

        while numPasses > 0: 
            
            self.sortingPass(bitPlane)
            self.refinementPass(bitPlane)
            bitPlane -= 1
            numPasses -= 1

        print(f'stopping theshold is {1 << bitPlane}')
        ##print(f'output is {self.encodedString}')
        return {'lis': self.lis, 'lsp' : self.lsp, 'lip' : self.lip, 'encodedStr' : self.encodedString}
    
    def compress(self, lsp = None, decompLevels = 3, numPasses = 3): 
        if lsp is None: 
            lsp = self.encodeSPIHT(decompLevels, numPasses)['lsp']
        compressedChannelMatrix = np.zeros(self.channelMatrix.shape)
        for i, j in lsp: 
            compressedChannelMatrix[i][j] = self.channelMatrix[i][j]
        return compressedChannelMatrix
    


channelMatrix = np.array([63, -34, 49, 10, 7, 13, -12, 7, -31, 23, 14, -13, 3, 4, 6, -1, 15, 14, 3, -12, 5, -7, 3, 9, -9, -7, -14, 8, 4, -2, 3, 2, -5, 9, -1, 47, 4, 6, -2, 2, 3, 0, -3, 2, 3, -2, 0, 4, 2, -3, 6, -4, 3, 6, 3, 6, 5, 11, 5, 6, 0, 3, -4, 4]).reshape((8, 8))

print(f'channel Matrix = \n {channelMatrix}')

spihtObj = SPIHT(channelMatrix)

#print(spihtObj.getDescendants((0, 0)))

##print(spihtObj.encodeSPIHT())
result = spihtObj.encodeSPIHT(decompLevels = 3, numPasses = 2)

for k,v in result.items(): 
    print(f'{k} - {v}')

print(result['lsp'])

