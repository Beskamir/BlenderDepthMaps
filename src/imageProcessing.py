import bpy
import os
import math
import numpy
import loadImage
#from .config import IMAGES_DIR

#References:
#   https://docs.blender.org/api/blender_python_api_2_71_release/bpy.types.Image.html
#   https://blender.stackexchange.com/questions/13422/crop-image-with-python-script/13516#13516
#   https://blender.stackexchange.com/questions/3673/why-is-accessing-image-data-so-slow/3678#3678
#   https://blender.stackexchange.com/questions/15890/is-it-possible-to-edit-images-programmatically-with-the-blender-api

#bpy.data.images.load("path\to\file.jpg")
IMAGES_DIR = "C:\\Program Files\\Blender Foundation\\Blender\\2.80\\scripts\\addons\\BlenderDepthMaps\\images"

# Some cheap enum replication using constants...
FRONT_FACE = 0
LEFT_FACE = 1
BACK_FACE = 2
RIGHT_FACE = 3
TOP_FACE = 4
BOTTOM_FACE = 5
FACES = [FRONT_FACE, LEFT_FACE, BACK_FACE, RIGHT_FACE, TOP_FACE, BOTTOM_FACE]

TOP_SIDE = 0
RIGHT_SIDE = 1
BOTTOM_SIDE = 2
LEFT_SIDE = 3
SIDES = [TOP_SIDE, RIGHT_SIDE, BOTTOM_SIDE, LEFT_SIDE]

# Using these values, we construct a dictionary that says which image connects to which on each one's borders.
# It is possible that, in the future, different rotations for the TOP_FACE and BOTTOM_FACE images may need to be considered.
BORDER_DICTIONARY = {
    FRONT_FACE: {
        # This first entry means that the top side of the front face's image corresponds to the bottom side of the top face's image.
        TOP_SIDE: {"face": TOP_FACE, "side": BOTTOM_SIDE},
        # The rest of the entries follow the same format.
        RIGHT_SIDE: {"face": RIGHT_FACE, "side": LEFT_SIDE},
        BOTTOM_SIDE: {"face": BOTTOM_FACE, "side": BOTTOM_SIDE},
        LEFT_SIDE: {"face": LEFT_FACE, "side": RIGHT_SIDE}
    },
    LEFT_FACE: {
        TOP_SIDE: {"face": TOP_FACE, "side": LEFT_SIDE},
        RIGHT_SIDE: {"face": FRONT_FACE, "side": LEFT_SIDE},
        BOTTOM_SIDE: {"face": BOTTOM_FACE, "side": RIGHT_SIDE},
        LEFT_SIDE: {"face": BACK_FACE, "side": RIGHT_SIDE}
    },
    BACK_FACE: {
        TOP_SIDE: {"face": TOP_FACE, "side": TOP_SIDE},
        RIGHT_SIDE: {"face": LEFT_FACE, "side": LEFT_SIDE},
        BOTTOM_SIDE: {"face": BOTTOM_FACE, "side": TOP_SIDE},
        LEFT_SIDE: {"face": RIGHT_FACE, "side": RIGHT_SIDE}
    },
    RIGHT_FACE: {
        TOP_SIDE: {"face": TOP_FACE, "side": RIGHT_SIDE},
        RIGHT_SIDE: {"face": BACK_FACE, "side": LEFT_SIDE},
        BOTTOM_SIDE: {"face": BOTTOM_FACE, "side": LEFT_SIDE},
        LEFT_SIDE: {"face": FRONT_FACE, "side": RIGHT_SIDE}
    },
    TOP_FACE: {
        TOP_SIDE: {"face": BACK_FACE, "side": TOP_SIDE},
        RIGHT_SIDE: {"face": RIGHT_FACE, "side": TOP_SIDE},
        BOTTOM_SIDE: {"face": FRONT_FACE, "side": TOP_SIDE},
        LEFT_SIDE: {"face": LEFT_FACE, "side": TOP_SIDE}
    },
    BOTTOM_FACE: {
        TOP_SIDE: {"face": BACK_FACE, "side": BOTTOM_SIDE},
        RIGHT_SIDE: {"face": LEFT_FACE, "side": BOTTOM_SIDE},
        BOTTOM_SIDE: {"face": FRONT_FACE, "side": BOTTOM_SIDE},
        LEFT_SIDE: {"face": RIGHT_FACE, "side": BOTTOM_SIDE}
    }
}

# Directions for iterating through the 3D and 2D arrays for each face.
iteration3D_Dictionary = {
    FRONT_FACE: {
        "vertical": (0,0,1),
        "horizontal": (0,1,0),
        "inwards": (-1,0,0)
    },
    LEFT_FACE: {
        "vertical": (0,0,1),
        "horizontal": (1,0,0),
        "inwards": (0, 1, 0)
    },
    BACK_FACE: {
        "vertical": (0,0,1),
        "horizontal": (0,-1,0),
        "inwards": (1,0,0)
    },
    RIGHT_FACE: {
        "vertical": (0,0,1),
        "horizontal": (-1,0,0),
        "inwards": (0, -1, 0)
    },
    TOP_FACE: {
        "vertical": (-1,0,0),
        "horizontal": (0,1,0),
        "inwards": (0,0,-1)
    },
    BOTTOM_FACE: {
        "vertical": (-1,0,0),
        "horizontal": (0,-1,0),
        "inwards": (0,0,1)
    }
}

# This function implements an outlier removal approach outlined in 
#       NIST/SEMATECH e-Handbook of Statistical Methods, http://www.itl.nist.gov/div898/handbook/, accessed on December 1, 2019.
# Specifically, this method is found in section "1.3.5.17. Detection of Outliers"
# Link: https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm
# Use of this method was inspired by a StackOverflow answer by Benjamin Bannier, in response to the question "Is there a numpy builtin to reject outliers from a list" asked by aaren.
# Link (Dec. 1, 2019): https://stackoverflow.com/a/16562028

def removeOutliers(arr, modifiedZScoreThreshold=3.5):
    dev = arr - numpy.median(arr)
    # "mad" = "Median Absolute Deviation"
    mad = numpy.median(numpy.abs(dev))
    if mad == 0:
        return arr
    modifiedZs = 0.6745*dev/mad
    return arr[numpy.abs(modifiedZs) <= modifiedZScoreThreshold]

# Marzullo's algorithm, which Keith Marzullo invented for his Ph.D. dissertation in 1984.
# https://en.wikipedia.org/wiki/Marzullo%27s_algorithm
# The algorithm finds the "relaxed intersection" that satisfies an optimal number of ranges.
# An intersection for ALL ranges may be impossible (e.g. some may be completely disjoint), 
# but Marzullo's algorithm will yield the intersection of as many as possible.
# 
# Returns the tuple (bestStart, bestEnd, best)
#   - bestStart: the start of the interval.
#   - bestEnd: the end of the interval.
#   - best: the number of intervals satisfied by this intersection.
def marzullo(upper, lower):

    # Assign a type of 1 to upper boundaries, -1 to lower boundaries
    ones = numpy.ones(upper.shape)
    minusOnes = numpy.full(lower.shape, -1.0)
    upperTuples = numpy.stack((upper, ones), axis=-1)
    lowerTuples = numpy.stack((lower, minusOnes), axis=-1)

    # Combine all boundaries, with their types, into a single table of tuples
    table = numpy.concatenate((upperTuples, lowerTuples))

    # Sorting by "first column" uses an answer by Steve Tjoa to the question "Sorting arrays in NumPy by Column", asked by user248237
    # Link: https://stackoverflow.com/a/2828121
    # Accessed Dec. 1, 2019
    table = table[table[:,0].argsort()]

    # Initialize
    # count is the number of intervals satisfied if we were to update bestStart and bestEnd for the new offset.
    # The others are described in the comment at the start of this function
    best = count = bestStart = bestEnd = 0
    for i in range(table.shape[0]):
        count -= table[i][1] # Subtract the type of the boundary from count
        if count > best:
            best = count
            bestStart = table[i][0]
            bestEnd = table[i+1][0] # Will never go out of bounds, since count>best is impossible for last boundary, which would be of type +1
    return (bestStart, bestEnd, best) 


class imageProcessor:
    # maxWidth is not actually used at the moment, but I plan to do something with it if there's time later.
    def __init__(self, originalFilenames, maxWidth=1024):
        self.imageLoader = loadImage.loadImage()
        self.createArrays(originalFilenames, maxWidth)

    # maxWidth is not actually used at the moment, but I plan to do something with it if there's time later.
    def createArrays(self, originalFilenames, maxWidth=1024):
        self.originalFilenames = originalFilenames
        self.maxWidth = maxWidth
        
        self.cropImages()
        print("Images cropped!")
        #self.resizeImages()
        #self.alignImages()

        self.setImageHeightRanges()
        print("Height ranges set!")
        self.generate3D()
        print("3D map generated!")
        return
    
    def cropImages(self):
        self.images2D = {}
        self.spaces = {}
        for face in FACES:
            # Load the image
            filename = self.originalFilenames[face]
            print("Loading:",filename)
            image = self.imageLoader.openImage(filename)
            #print(image)
            print("---------\n"+filename, "has been converted into a 2D array.")
            # Crop the 2D-list "image" to remove all-alpha border regions
            # Also, store the number of alpha pixels that buffer each row/column for use in a later stage.
            alphas = image[:,:,3]
            # Sum the alphas for each column; if the sum == 0, then the entire column is transparent.
            colSum = alphas.sum(axis=0) # Each column -> one sum
            rowSum = alphas.sum(axis=1) # Each row -> one sum
            nonzeroCols = colSum.nonzero()[0]
            nonzeroRows = rowSum.nonzero()[0]
            # Crop the image by slicing from the first index of nonzeroRows to the last, and the same for columns
            image = image[nonzeroRows[0]:nonzeroRows[-1]+1, nonzeroCols[0]:nonzeroCols[-1]+1]

            newAlphas = image[:,:,3]

            # Access the image's alpha and create an array of bools that state whether the alpha is zero or not 
            visibles = ((newAlphas) != 0)
            # Now, we get the number of transparent pixels we must traverse over, from the left, in each row until we hit the "object", i.e. a nontransparent pixel
            # This information will allow us to fit "neighbouring" images' height ranges to match this "outline"
            topSpaces = (visibles[::-1,:]!=0).argmax(axis=0)
            rightSpaces = (visibles[:,::-1]!=0).argmax(axis=1)
            bottomSpaces = (visibles!=0).argmax(axis=0)
            leftSpaces = (visibles!=0).argmax(axis=1)
            print("----------")
            for s in [topSpaces, rightSpaces, bottomSpaces, leftSpaces]:
                print("space shape:", s.shape)

            '''
            # Now, we add a float component to the spaces based on the border pixel's transparency
            rowIndices = numpy.indices((newAlphas.shape[0],))
            colIndices = numpy.indices((newAlphas.shape[1],))
            #Top
            topSpaces = topSpaces + 1-newAlphas[newAlphas.shape[0] - 1 - topSpaces, colIndices]
            #Right
            rightSpaces = rightSpaces + 1-newAlphas[rowIndices, newAlphas.shape[1] - 1 - rightSpaces]
            #Bottom
            bottomSpaces = bottomSpaces + 1-newAlphas[bottomSpaces, colIndices]
            #Left
            leftSpaces = leftSpaces + 1-newAlphas[rowIndices, leftSpaces]
            '''

            self.spaces[face] = {
                TOP_SIDE: topSpaces.flatten(),
                RIGHT_SIDE: rightSpaces.flatten(),
                BOTTOM_SIDE: bottomSpaces.flatten(),
                LEFT_SIDE: leftSpaces.flatten()
            }

            print("----------")
            for side in SIDES:
                print("space shape NEW:", self.spaces[face][side].shape)


            self.images2D[face] = image
            '''
            print(face, "---------------------")
            print("cropLeft:", cropLeft)
            print("cropRight:", cropRight)
            print("cropTop:", cropTop)
            print("cropBottom:", cropBottom)
            '''
            '''
            for xp in range(len(image)-1, -1, -1):
                for yp in range(len(image[xp])):
                    pixel = image[xp][yp]
                    if pixel[3] <= 0:
                        print("___", end=", ")
                    else:
                        print(pixel[0], end=", ")
                print("\n_ _ _ _ _ _ _")
            '''
        self.xLen = self.images2D[TOP_FACE].shape[0]
        self.yLen = self.images2D[FRONT_FACE].shape[1]
        self.zLen = self.images2D[FRONT_FACE].shape[0]

        return
        

    def setImageHeightRanges(self):
        self.depthDictionary = {}
        for i in FACES:
            self.setImageHeightRangeSingle(i)
        for face in FACES:
            print("\nFace info for face", face, ":")
            d = self.depthDictionary[face]
            print("highestFloat:", d["highestFloat"], "\nhighestCellDepth:", d["highestCellDepth"], "\nlowestFloat:", d["lowestFloat"], "\nlowestCellDepth:", d["lowestCellDepth"])
            print()
        return

    def setImageHeightRangeSingle(self, selectedFace):
        selectedImage = self.images2D[selectedFace]
        # The heights can be seen as a negation of the r, g, or b channel of the image
        # We'll choose the r channel
        # Negation because, with depth maps, darker = closer = "higher"
        # Old versions of this code used (1 - pixel) instead of negation, until we realized that exr images map outside the range [0,1]
        # Negation's a more readable alternative, with this in mind.
        # And from the math side, all that matters is the relative linear ranges between pixels
        heights = -selectedImage[:,:,0]
        alphas = selectedImage[:,:,3]
        transparentIndices = (alphas < 1)
        visibleIndices = (alphas == 1)
        # Set all transparent pixels' heights to negative infinity, so they don't get considered for "max"
        heights[transparentIndices] = numpy.NINF # NINF = "Negative INFinity"
        
        maxPerCol = numpy.amax(heights, axis=0)
        print("\nFACE:", selectedFace)
        print("maxPerCol.shape:", maxPerCol.shape)
        maxPerRow = numpy.amax(heights, axis=1)
        print("maxPerRow.shape:", maxPerRow.shape)

        maxHeight = numpy.amax(heights) # No axis means just returning a single max
        minHeight = numpy.amin(heights[visibleIndices])
        print("Min and Max height, respectively:", (minHeight, maxHeight))
        heightRange = maxHeight - minHeight

        # We'll create a list of upper & lower bounds that would allow each row/column to "fit" with the outline in the neighbouring image
        upperRangesPerSide = []
        lowerRangesPerSide = []

        for side in SIDES:
            # Row maxes are visible from left/right neighbour images. Column maxes are visible from top/bottom neighbours.
            maxes = maxPerRow
            if side == TOP_SIDE or side == BOTTOM_SIDE:
                maxes = maxPerCol
            # Get the neighbour on this side from our dictionary at the top of this file.
            neighbourFace = BORDER_DICTIONARY[selectedFace][side]["face"]
            neighbourSide = BORDER_DICTIONARY[selectedFace][side]["side"]
            spaces = self.spaces[neighbourFace][neighbourSide]

            # The "depth" of a point, calculated later, will be (maxHeight - h)/(maxHeight-minHeight) times the total number of cells the face's depth should span.
            #      (Here, "h" is a height in maxPerRow or maxPerCol, meaning it'll be visible from the corresponding neighbouring depth maps.)
            # To line up the images, this "depth" should equal the number of transparent pixels, e.g. "spaces", it takes to "reach" the object in a corresponding row or col of a corresponding neighbour image
            # This way, we'll get the outline of the object correct.
            # If we re-arrange this equality, we get cellRange = spaces*(maxHeight-minHeight)/(maxHeight - h)
            # Of course, there's also rounding at play, which means we'll actually look for a span of values that would satisfy cellRange
            # This will be commented on a bit more below.

            # These are the (maxHeight - h) values
            diffsFromMax = maxHeight - maxes

            # Our division will only be defined when (maxHeight - h) != 0. Find these indices.
            validIndices = diffsFromMax.nonzero()
            spacesValid = spaces[validIndices]
            diffsValid = diffsFromMax[validIndices]

            # Spaces of zero (or that'd round to zero) also don't matter, since they'll be trivially mapped to 0 cells deep regardless
            relevant = spacesValid.nonzero() #spacesValid.floor().nonzero()
            spacesRelevant = spacesValid[relevant]
            diffsRelevant = diffsValid[relevant]

            # Since the "spaces"/pixels are at discrete intervals, we don't need to match them exactly.
            # We should just match some number that would round to them. 
            # We'll use a tolerance of 0.49 on each side; almost half, but a bit less to accomodate floating point precision issues and other stuff.
            tolerance = 1.49

            upperRangesForThisSide = heightRange * (spacesRelevant + tolerance) / diffsRelevant
            lowerRangesForThisSide = heightRange * (spacesRelevant - tolerance) / diffsRelevant
            # For the lower, we also want to make sure we don't say that the range could be negative.
            # Replace all negative values with zero.
            lowerRangesForThisSide = lowerRangesForThisSide.clip(min=0)

            upperRangesPerSide.append(upperRangesForThisSide)
            lowerRangesPerSide.append(lowerRangesForThisSide)
            

        upperCellRanges = numpy.concatenate(tuple(upperRangesPerSide))
        lowerCellRanges = numpy.concatenate(tuple(lowerRangesPerSide))
        
        bestBoundary = marzullo(upperCellRanges, lowerCellRanges)
        print("Satisfied boundaries:", bestBoundary[2], "/", len(upperCellRanges), ".")
        guessRange = (bestBoundary[0] + bestBoundary[1])/2

        '''
        print("Ranges for face", selectedFace, ":")
        print(cellRanges)
        print("Min and max suggested ranges:", (numpy.amin(cellRanges), numpy.amax(cellRanges)))
        print("Nonzero entries:", numpy.count_nonzero(cellRanges), "/", cellRanges.shape[0])
        guessRange = round(numpy.median(cellRanges))
        '''

        self.depthDictionary[selectedFace] = {
            "highestFloat": maxHeight,
            "highestCellDepth": 0,
            "lowestFloat": minHeight,
            "lowestCellDepth": guessRange
        }
        return

    

    def generate3D(self):
        # For ease of typing
        zLen = self.zLen
        yLen = self.yLen
        xLen = self.xLen

        structureInfo = {
            FRONT_FACE: {
                "depthAxisLen":  xLen,
                "axisPermutation": (2,0,1)
            },
            LEFT_FACE: {
                "depthAxisLen":  yLen,
                "axisPermutation": (0,2,1)
            },
            BACK_FACE: {
                "depthAxisLen":  xLen,
                "axisPermutation": (2,0,1)
            },
            RIGHT_FACE: {
                "depthAxisLen":  yLen,
                "axisPermutation": (0,2,1)
            },
            TOP_FACE: {
                "depthAxisLen":  zLen,
                "axisPermutation": (1,0,2)
            },
            BOTTOM_FACE: {
                "depthAxisLen":  zLen,
                "axisPermutation": (1,0,2)
            }
        }

        self.points3D = {} 
        print("Array initialized.")
        for face in FACES:
            image = self.images2D[face]
            # Get an array of indices
            # iList[0] will contain the row indices, while iList[1] will contain the column indices
            iList = numpy.indices((image.shape[0], image.shape[1]))
            rowIndices = iList[0]
            colIndices = iList[1]

            # "flip" the indices if necessary, depending on which face we're viewing them from
            if face == BACK_FACE or face == RIGHT_FACE or face == BOTTOM_FACE:
                imageWidth = image.shape[1]
                horizFlip = lambda x: imageWidth - 1 - x
                colIndices = horizFlip(colIndices)
            if face == TOP_FACE or face == BOTTOM_FACE:
                imageHeight = image.shape[0]
                vertFlip = lambda y: imageHeight - 1 - y
                rowIndices = vertFlip(rowIndices)

            highestFloat = self.depthDictionary[face]["highestFloat"]
            lowestFloat = self.depthDictionary[face]["lowestFloat"]
            highestCellDepth = self.depthDictionary[face]["highestCellDepth"]
            lowestCellDepth = self.depthDictionary[face]["lowestCellDepth"]
            depthRange = highestFloat - lowestFloat
            if depthRange == 0.0:
                print("REMINDER: ALLOW USER-INPUT MODIFICATION FOR CASE WHERE DEPTH RANGE MAPPING CANNOT BE AUTOMATICALLY DETERMINED!")
                print("SETTING DEFAULT DEPTH RANGE AS TEMPORARY DEFAULT!")
                depthRange = 1.0

            depthify = lambda pixelHeight: ((highestFloat-pixelHeight)*lowestCellDepth + (pixelHeight - lowestFloat)*highestCellDepth)/depthRange
            # Negate the image, since we want darker values to be "higher"
            depths = depthify(-image[:,:,0])
            depths = depths.round()

            alphas = image[:,:,3]
            visibles = numpy.nonzero(alphas)

            # May also need to "flip" this depth image
            if face == FRONT_FACE or face == RIGHT_FACE or face == TOP_FACE:
                imageDepth = structureInfo[face]["depthAxisLen"]
                print("Image depth for face", face, ":", imageDepth)
                print("Max:", numpy.max(depths[visibles]))
                print("Min:", numpy.min(depths[visibles]))
                depthFlip = lambda d: imageDepth - 1 - d
                depths = depthFlip(depths)

            coordLists = [colIndices,rowIndices,depths]
            permutation = structureInfo[face]["axisPermutation"]
            reorderedCoordLists = (coordLists[permutation[0]], coordLists[permutation[1]], coordLists[permutation[2]])
            # Now stack to create a list containing elements of the form (rowIndex, colIndex, height, alpha)
            
            '''print("Image shape:", image.shape)
            print("x shape:", coordLists[permutation[0]].shape)
            print("y shape:", coordLists[permutation[1]].shape)
            print("z shape:", coordLists[permutation[2]].shape)
            print("alpha shape:", image[:,:,3].shape)'''

            stackedList = numpy.stack(reorderedCoordLists, axis=-1)
            
            pointsList = stackedList[visibles]
            
            
            self.points3D[face] = pointsList
            print("Done one face.")
        #self.points3D = numpy.array(points3D)
        #self.points3D = numpy.unique(self.points3D, axis=0)
        return

    def generateArray3D(self):
        # For ease of typing
        zLen = self.zLen
        yLen = self.yLen
        xLen = self.xLen
        

        # A quick "in bounds" function that states whether a coordinate is within the dimensions of our 3D array.
        inBounds = lambda coord: coord[0] >= 0 and coord[0] < xLen and coord[1] >= 0 and coord[1] < yLen and coord[2] >= 0 and coord[2] < zLen
        # Lambda for elementwise adding two tuples of length 3
        add = lambda x, y: (x[0] + y[0], x[1] + y[1], x[2] + y[2])
        constMult = lambda k, vec: (k*vec[0], k*vec[1], k*vec[2])

        # Dictionary of "starting positions" for iteration for each face.
        # For each pixel in each face's image, we'll traverse "inwards" through the 3D array.
        # So, for the coordinates corresponding to pixel selection, we'll start at 0 and 0 (e.g. for FACE_FRONT, y = 0 and z = 0)
        # For the coordinate corresponding to the "depth" coordinate for the face, we'll start at either 0 or the "max" for that direction.
        # E.g. for FRONT_FACE, we start at x = (xLen - 1) and end at x=0.
        startDict = {
            FRONT_FACE: (xLen-1, 0, 0),
            LEFT_FACE: (0,0,0),
            BACK_FACE: (0,yLen-1,0),
            RIGHT_FACE: (xLen-1,yLen-1,0),
            TOP_FACE: (xLen-1,0,zLen-1),
            BOTTOM_FACE: (xLen-1,yLen-1,0)
        }
        # We'll do two phases.
        # First, we'll do all "definitive" cells, with alpha values zero or one.
        # Then, we'll do all partial-alpha cells IF there's no conflict.
        # March, for each pixel on each "face" of the surrounding cube, inwards and replace 1's with 0's (edge) and -1's (outside) values wherever alpha is strictly 0 or 1.
        
        OUTSIDE = 1
        BOUNDARY = 0
        INSIDE = -1
        self.object3D = numpy.full((xLen, yLen, zLen), INSIDE)
        
        for face in FACES:
            highestFloat = self.depthDictionary[face]["highestFloat"]
            lowestFloat = self.depthDictionary[face]["lowestFloat"]
            highestCellDepth = self.depthDictionary[face]["highestCellDepth"]
            lowestCellDepth = self.depthDictionary[face]["lowestCellDepth"]
            depthRange = highestFloat - lowestFloat
            if depthRange == 0.0:
                print("REMINDER: ALLOW USER-INPUT MODIFICATION FOR CASE WHERE DEPTH RANGE MAPPING CANNOT BE AUTOMATICALLY DETERMINED!")
                print("SETTING DEFAULT DEPTH RANGE AS TEMPORARY DEFAULT!")
                depthRange = 1.0

           

            pixelXIndex = 0
            pixelYIndex = 0

            if depthRange <= 0:
                # The actual logic happens deeper inside the while loop. Look for it below, marked with "#updateme"
                print("REMINDER: ALLOW USER-INPUT MODIFICATION FOR CASE WHERE DEPTH RANGE MAPPING CANNOT BE AUTOMATICALLY DETERMINED!")
                print("SETTING ALL VALUES TO 'MAX' AS TEMPORARY DEFAULT!")
            index = startDict[face] # Convert into list so that it's mutable

            while inBounds(index):
                refIndexHoriz = index # Save current index before the "vert" and "inwards" coords are altered
                while inBounds(index):
                    refIndexVert = index # Save current index before the "inwards" coord is altered
                    depth = 0
                    
                    pixelVal = self.images2D[face][pixelYIndex][pixelXIndex]
                    # The negation is to represent the higher, darker pixels with higher/larger floats, to be consistent with other parts of this code
                    pixelHeight = -pixelVal[0]
                    pixelAlpha = pixelVal[3]
                    if depthRange == 0:
                        #updateme
                        depthCap = highestCellDepth
                    else:
                        depthCap = round(((highestFloat-pixelHeight)*lowestCellDepth + (pixelHeight - lowestFloat)*highestCellDepth)/depthRange)
                    '''if pixelAlpha > 0:
                        #print("index:", index)
                        #print("depthCap:", depthCap)
                        depthToTraverse = constMult(depthCap, iteration3D_Dictionary[face]["inwards"])
                        #print("depthToTraverse:", depthToTraverse)
                        cubeIndex = add(index, depthToTraverse)
                        #print("CubeIndex:", cubeIndex)
                        points3D.append(cubeIndex)
                        #print("\n][][][][][\n")'''
                    '''
                    '''
                    # Make sure we don't overwrite a "definitive" value from a previous face's phase
                    makeOutside = lambda x: abs(x)
                    if INSIDE == 1 and OUTSIDE == -1:
                        makeOutside = lambda x: -abs(x)

                    # Alpha check
                    if pixelAlpha > 0:
                        endIndex = add(index, constMult(depthCap, iteration3D_Dictionary[face]["inwards"]))
                        x1 = int(index[0])
                        x2 = int(endIndex[0])
                        y1 = int(index[1])
                        y2 = int(endIndex[1])
                        z1 = int(index[2])
                        z2 = int(endIndex[2])
                        #rint("INDICES:", x1, x2, y1, y2, z1, z2)
                        self.object3D[x1:x2, y1:y2, z1:z2] = makeOutside(self.object3D[x1:x2, y1:y2, z1:z2] )
                        index = add((x2,y2,z2), iteration3D_Dictionary[face]["inwards"])
                        if inBounds(index):
                            #print("BOUNDARY:", index)
                            self.object3D[index] = BOUNDARY # BOUNDARY = 0
                    elif pixelAlpha == 0:
                        allDepth = xLen
                        if face == LEFT_FACE or face == RIGHT_FACE:
                            allDepth = yLen
                        if face == TOP_FACE or face == BOTTOM_FACE:
                            allDepth = zLen

                        endIndex = add(index, constMult(allDepth,iteration3D_Dictionary[face]["inwards"]))
                        x1 = int(index[0])
                        x2 = int(endIndex[0])
                        y1 = int(index[1])
                        y2 = int(endIndex[1])
                        z1 = int(index[2])
                        z2 = int(endIndex[2])
                        self.object3D[x1:x2, y1:y2, z1:z2] = makeOutside(self.object3D[x1:x2, y1:y2, z1:z2] )                        
                        '''while inBounds(index):
                            if self.object3D[index] == INSIDE:
                                self.object3D[index] = OUTSIDE # OUTSIDE'''
                            
                
                    '''
                    '''
                    # reset "inwards" and increment "vert"
                    index = add(refIndexVert, iteration3D_Dictionary[face]["vertical"])
                    pixelYIndex += 1
                # reset "vert" and "inwards" and increment "horiz"
                index = add(refIndexHoriz, iteration3D_Dictionary[face]["horizontal"])
                pixelXIndex += 1
                pixelYIndex = 0
                #print("Done a slice.")
            
            print("Done one face.")
        #self.points3D = numpy.array(points3D)
        #self.points3D = numpy.unique(self.points3D, axis=0)
        return self.object3D




if __name__ == "__main__":
    # Test function
    TEST_IMAGE_PATH_PREFIX = "LightPathDistance\\Torus\\" #"lowres\\ch_"
    TEST_IMAGE_PATH_SUFFIX = ".png"
    imageNames = []
    for i in range(6):
        imageNames.append(os.path.join(IMAGES_DIR, TEST_IMAGE_PATH_PREFIX + str(i) + TEST_IMAGE_PATH_SUFFIX))
    image = imageProcessor(imageNames)
    
    '''print("Printing slices along the x-axis")
    for x in range(image.xLen):
        print("Slice for x =", x)
        print("==================")
        for z in range(image.zLen-1, -1, -1):
            for y in range(image.yLen):
                cellVal = image.object3D[x][y][z]
                printVal = "#"
                if cellVal > 0:
                    printVal = "."
                elif cellVal < 0:
                    printVal = " " 
                print(printVal, end=" ")
            print("\n-----------------")
        print("\n")'''
    print("Done imageProcessing.py test.")
