import bpy
import os
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


class imageProcessor:
    # maxWidth is not actually used at the moment, but I plan to do something with it if there's time later.
    def __init__(self, originalFilenames, maxWidth=1024):
        self.imageLoader = loadImage.loadImage()
        self.createArrays(originalFilenames, maxWidth)

    '''# Blender stores images as 1D arrays, ordered as described in https://blender.stackexchange.com/questions/13422/crop-image-with-python-script/13516#13516
    # This function generates a 2D array of (r,g,b,a) tuples from said 1D list
    # Calling the result at index [i][j] will return the pixel in the i-th row from the bottom, j-th column from the left
    # i.e. where i=j=0 is the bottom-left pixel.
    def blenderImageToTwoD(self, blenderImage):
        x = blenderImage.size[0]
        y = blenderImage.size[1]
        image = numpy.empty(shape=(x,y), dtype=(float,4))
        index = 0
        for i in range(x):
            for j in range(y):
                r = blenderImage.pixels[index]
                g = blenderImage.pixels[index+1]
                b = blenderImage.pixels[index+2]
                a = blenderImage.pixels[index+3]
                # Apparently, in blender images, lower alpha -> "darker"
                if a > 0:
                    r = r/a
                    g = g/a
                    b = b/a
                image[i][j] = (r,g,b,a)
                index += 4
        return image'''

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
        self.images2D = []
        for i in FACES:
            # Load the image
            filename = self.originalFilenames[i]
            print("Loading:",filename)
            image = self.imageLoader.openImage(filename)
            print("---------\n"+filename, "has been converted into a 2D array.")
            # Crop the 2D-list "image" to remove all-alpha border regions
            # LEFT
            cropLeft = 0
            foundPosAlpha = False
            while not foundPosAlpha:
                for j in range(len(image)):
                    if image[j][cropLeft][3] > 0.0:
                        foundPosAlpha = True
                        break
                if foundPosAlpha:
                    break
                else:
                    cropLeft += 1
            # RIGHT
            cropRight = len(image[0])-1
            foundPosAlpha = False
            while not foundPosAlpha:
                for j in range(len(image)):
                    if image[j][cropRight][3] > 0.0:
                        foundPosAlpha = True
                        break
                if foundPosAlpha:
                    break
                else:
                    cropRight -= 1
            # TOP
            cropTop = len(image)-1
            foundPosAlpha = False
            while not foundPosAlpha:
                for j in range(len(image[0])):
                    if image[cropTop][j][3] > 0.0:
                        foundPosAlpha = True
                        break
                if foundPosAlpha:
                    break
                else:
                    cropTop -= 1
            # BOTTOM
            cropBottom = 0
            foundPosAlpha = False
            while not foundPosAlpha:
                for j in range(len(image[0])):
                    if image[cropBottom][j][3] > 0.0:
                        foundPosAlpha = True
                        break
                if foundPosAlpha:
                    break
                else:
                    cropBottom += 1
            image = [image[i][cropLeft:cropRight+1] for i in range(cropBottom,cropTop+1)] 
            self.images2D.append(image)
            print(i, "---------------------")
            print("cropLeft:", cropLeft)
            print("cropRight:", cropRight)
            print("cropTop:", cropTop)
            print("cropBottom:", cropBottom)
            '''for xp in range(len(image)-1, -1, -1):
                for yp in range(len(image[xp])):
                    pixel = image[xp][yp]
                    if pixel[3] <= 0:
                        print("___", end=", ")
                    else:
                        print(pixel[0], end=", ")
                print("\n_ _ _ _ _ _ _")'''
        self.xLen = len(self.images2D[TOP_FACE])
        self.yLen = len(self.images2D[FRONT_FACE][0])
        self.zLen = len(self.images2D[FRONT_FACE])

        return
        

    def setImageHeightRanges(self):
        self.depthDictionary = {}
        for i in FACES:
            self.setImageHeightRangeSingle(i)
        for face in FACES:
            print("Face info for face", face, ":")
            d = self.depthDictionary[face]
            print("highestFloat:", d["highestFloat"], "\nhighestCellDepth:", d["highestCellDepth"], "\nlowestEdgeFloat:", d["lowestEdgeFloat"], "\nlowestEdgeCellDepth:", d["lowestEdgeCellDepth"])
            print()
        return
    
    def setImageHeightRangeSingle(self, selectedFace):
        selectedImage = self.images2D[selectedFace]
        # First, find 1 minus the "highest" pixel's value
        # (The 1 minus is because darker pixels are higher, but it's more intuitive to encode higher values as, well, higher floats)
        highest = 0.0
        for i in range(len(selectedImage)):
            for j in range(len(selectedImage[i])):
                # Check the pixel's alpha, to ensure pixel is not transparent.
                if selectedImage[i][j][3] > 0:
                    # Choose any of the RGB channels for height comparison
                    if (1-selectedImage[i][j][0]) > highest:
                        highest = (1-selectedImage[i][j][0])
        # Then, from ANY "side" reference image, find out where this max value occurs.
        # We'll choose the image from the top side.
        correspondingFace = BORDER_DICTIONARY[selectedFace][TOP_SIDE]["face"]
        correspondingFaceImage = self.images2D[correspondingFace]
        correspondingSide = BORDER_DICTIONARY[selectedFace][TOP_SIDE]["side"]
        depthInwardsHighest = 0
        foundOpaque = False
        # First, we handle the case for when correspondingSide is LEFT or RIGHT 
        if correspondingSide == LEFT_SIDE or correspondingSide == RIGHT_SIDE:
            columnToSearch = 0
            colIncrement = 1
            if correspondingSide == RIGHT_SIDE:
                columnToSearch = len(correspondingFaceImage[0])-1
                colIncrement = -1
            # Search column-by-column until we find something opaque.
            while not foundOpaque:
                for row in range(len(correspondingFaceImage)):
                    if correspondingFaceImage[row][columnToSearch][3] > 0.0:
                        foundOpaque = True
                        break
                if not foundOpaque:
                    columnToSearch += colIncrement
                    depthInwardsHighest += 1
        # THEN, we handle the case for when correspondingSide is TOP or BOTTOM
        else:
            rowToSearch = 0
            rowIncrement = 1
            if correspondingSide == TOP_SIDE:
                rowToSearch = len(correspondingFaceImage)-1
                rowIncrement = -1
            # Search row-by-row until we find something opaque.
            while not foundOpaque:
                for col in range(len(correspondingFaceImage[rowToSearch])):
                    if correspondingFaceImage[rowToSearch][col][3] > 0.0:
                        foundOpaque = True
                        break
                if not foundOpaque:
                    rowToSearch += rowIncrement
                    depthInwardsHighest += 1

        # Then, find the "lowest" pixel's value ON THE OUTERMOST EDGE(S) OF THE OBJECT!
        #   (i.e. not "lowest" pixel overall, as that may correspond to indents that are invisible from other angles)
        #   ALSO, keep track of which of the four "sides" this point's "edge" will be visible from
        # Set default/starting values for the info to keep track of
        lowestEdge = 1.0
        lowestSide = TOP_SIDE # Random default; could have just as well been LEFT, RIGHT, or BOTTOM_SIDE.
        # First, the left and right sides are tested.
        # (We also do checks on indices in case we somehow, in spite of prior cropping, end up with an all-transparent row)
        for row in range(len(selectedImage)):
            #Test from the left
            leftColumn = 0
            while leftColumn < len(selectedImage[row]) and selectedImage[row][leftColumn][3] <= 0:
                leftColumn += 1
            rightColumn = len(selectedImage[row]) - 1
            while rightColumn >= 0 and selectedImage[row][rightColumn][3] <= 0:
                rightColumn -= 1
            if leftColumn < len(selectedImage[row]) and (1-selectedImage[row][leftColumn][0]) < lowestEdge:
                lowestEdge = (1-selectedImage[row][leftColumn][0])
                lowestSide = LEFT_SIDE
            if rightColumn >= 0 and (1-selectedImage[row][rightColumn][0]) < lowestEdge:
                lowestEdge = (1-selectedImage[row][rightColumn][0])
                lowestSide = RIGHT_SIDE
        # Then, the top and bottom sides are tested.
        # (We also do checks on indices in case we somehow, in spite of prior cropping, end up with an all-transparent column)
        for column in range(len(selectedImage[0])):
            #Test from the top
            topRow = len(selectedImage) - 1
            while topRow >= 0 and selectedImage[topRow][column][3] <= 0:
                topRow -= 1
            bottomRow = 0
            while bottomRow < len(selectedImage) and selectedImage[bottomRow][column][3] <= 0:
                bottomRow += 1
            if topRow >= 0 and (1-selectedImage[topRow][column][0]) < lowestEdge:
                lowestEdge = (1-selectedImage[topRow][column][0])
                lowestSide = TOP_SIDE
            if bottomRow < len(selectedImage) and (1-selectedImage[bottomRow][column][0]) < lowestEdge:
                lowestEdge = (1-selectedImage[bottomRow][column][0])
                lowestSide = BOTTOM_SIDE

        # Then, from THE "side" reference image corresponding to the "lowestEdge" pixel's value
        #   This is, as may be expected, the most complicated part.
        #   We will have to approach it as follows:
        #       Let A represent the image we're analyzing with this call to setImageHeightRangeSingle()
        #       Let B represent the "side" reference image we're using to try and find the lower value in A.
        #       For this example, assume A and B are "joined" on the right edge of B.
        #       Then, for each row of B, we find the darkest ("highest") pixel, and keep track of which column it belongs to.
        #           If there's ever a "tie", we keep the rightmost tied pixel, since that's the one that'd be visible from A in this example.
        #       After doing this for each row, we choose the pixel furthest away from the right edge as our "match", in this example.
        #           Again, if there are ties HERE, it doesn't matter, since we only care about distance from the joining edge
        #       Now, the distance from this pixel to the right edge will be the depthInwardsLowest value we choose.
        correspondingFace = BORDER_DICTIONARY[selectedFace][lowestSide]["face"]
        correspondingFaceImage = self.images2D[correspondingFace]
        correspondingSide = BORDER_DICTIONARY[selectedFace][lowestSide]["side"]
        depthInwardsLowest = 0
        # First, we handle the case for when correspondingSide is LEFT or RIGHT 
        if correspondingSide == LEFT_SIDE or correspondingSide == RIGHT_SIDE:
            print("LEFT/RIGHT for face", selectedFace)
            startIndex = 0
            colIncrement = 1
            if correspondingSide == RIGHT_SIDE:
                startIndex = len(correspondingFaceImage[0])-1
                colIncrement = -1
            print("INCREMENT:", colIncrement)
            columnToSearch = startIndex
            # This array will keep track of the max height found in each row, and where it is.
            rowMaxes = [ { "val": 0.0, "depth":startIndex } ] * len(correspondingFaceImage)
            # Search column-by-column until we find something opaque.
            while columnToSearch in range(len(correspondingFaceImage[0])):
                for row in range(len(correspondingFaceImage)):
                    # Alpha check & comparing with current max
                    if correspondingFaceImage[row][columnToSearch][3] > 0.0 and (1-correspondingFaceImage[row][columnToSearch][0]) > rowMaxes[row]["val"]:
                        rowMaxes[row]["val"] = (1-correspondingFaceImage[row][columnToSearch][0])
                        rowMaxes[row]["depth"] = columnToSearch
                columnToSearch += colIncrement
            # Now, we set depthInwardsLowest to be the greatest distance from the edge observed in rowMaxes.
            for r in rowMaxes:
                curDist = abs(r["depth"] - startIndex)
                if curDist > depthInwardsLowest:
                    depthInwardsLowest = curDist
        # THEN, we handle the case for when correspondingSide is TOP or BOTTOM
        else:
            print("TOP/BOTTOM for face", selectedFace)
            startIndex = 0
            rowIncrement = 1
            if correspondingSide == TOP_SIDE:
                startIndex = len(correspondingFaceImage)-1
                rowIncrement = -1
            print("INCREMENT:", rowIncrement)
            rowToSearch = startIndex
            # This array will keep track of the max height found in each column, and where it is.
            colMaxes = [ { "val": 0.0, "depth":startIndex } ] * len(correspondingFaceImage[0])
            # Search row-by-row until we find something opaque.
            while rowToSearch in range(len(correspondingFaceImage)):
                for col in range(len(correspondingFaceImage[0])):
                    # Alpha check & comparing with current max
                    if correspondingFaceImage[rowToSearch][col][3] > 0.0 and (1-correspondingFaceImage[rowToSearch][col][0]) > colMaxes[col]["val"]:
                        colMaxes[col]["val"] = (1-correspondingFaceImage[rowToSearch][col][0])
                        colMaxes[col]["depth"] = rowToSearch
                        #print("Updating at row:", rowToSearch)
                rowToSearch += rowIncrement
            # Now, we set depthInwardsLowest to be the greatest distance from the edge observed in colMaxes.
            for c in colMaxes:
                #print("colMax:", c)
                curDist = abs(c["depth"] - startIndex)
                if curDist > depthInwardsLowest:
                    depthInwardsLowest = curDist
        self.depthDictionary[selectedFace] = {
            "highestFloat": highest,
            "highestCellDepth": depthInwardsHighest,
            "lowestEdgeFloat": lowestEdge,
            "lowestEdgeCellDepth": depthInwardsLowest
        }
        return

    def generate3D(self):
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
        points3D = []
        #self.object3D = numpy.ones(shape=(xLen,yLen,zLen)) # Fill with inside value (1)
        print("Array initialized.")
        # We'll do two phases.
        # First, we'll do all "definitive" cells, with alpha values zero or one.
        # Then, we'll do all partial-alpha cells IF there's no conflict.
        for phase in range(2):
            # March, for each pixel on each "face" of the surrounding cube, inwards and replace 1's with 0's (edge) and -1's (outside) values wherever alpha is strictly 0 or 1.
            for face in FACES:
                pixelXIndex = 0
                pixelYIndex = 0
                highestFloat = self.depthDictionary[face]["highestFloat"]
                lowestEdgeFloat = self.depthDictionary[face]["lowestEdgeFloat"]
                highestCellDepth = self.depthDictionary[face]["highestCellDepth"]
                lowestEdgeCellDepth = self.depthDictionary[face]["lowestEdgeCellDepth"]
                depthRange = highestFloat - lowestEdgeFloat
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
                        # The "1 - " is to represent the higher, darker pixels with higher/larger floats, to be consistent with other parts of this code
                        pixelHeight = 1-pixelVal[0]
                        pixelAlpha = pixelVal[3]
                        if depthRange == 0:
                            #updateme
                            depthCap = highestCellDepth
                        else:
                            depthCap = round(((highestFloat-pixelHeight)*lowestEdgeCellDepth + (pixelHeight - lowestEdgeFloat)*highestCellDepth)/depthRange)
                        if pixelAlpha > 0:
                            #print("index:", index)
                            #print("depthCap:", depthCap)
                            depthToTraverse = constMult(depthCap, iteration3D_Dictionary[face]["inwards"])
                            #print("depthToTraverse:", depthToTraverse)
                            cubeIndex = add(index, depthToTraverse)
                            #print("CubeIndex:", cubeIndex)
                            points3D.append(cubeIndex)
                            #print("\n][][][][][\n")
                        '''
                        # Alpha check
                        if pixelAlpha == 1 and phase == 0:
                            while inBounds(index) and depth < depthCap:
                                if self.object3D[index] == 1:
                                    self.object3D[index] = -1 # OUTSIDE = -1
                                index = add(index, iteration3D_Dictionary[face]["inwards"])
                                depth += 1
                            if inBounds(index):
                                self.object3D[index] = 0 # BOUNDARY = 0
                        elif pixelAlpha == 0 and phase == 0:
                            while inBounds(index):
                                if self.object3D[index] == 1:
                                    self.object3D[index] = -1 # OUTSIDE = -1
                                index = add(index, iteration3D_Dictionary[face]["inwards"])
                        elif pixelAlpha != 0 and pixelAlpha != 1 and phase == 1:
                            while inBounds(index) and depth < depthCap:
                                # Make sure we don't overwrite a "definitive" value from first phase
                                if self.object3D[index] == 1:
                                    self.object3D[index] = -1 # OUTSIDE = -1
                                index = add(index, iteration3D_Dictionary[face]["inwards"])
                                depth += 1
                            # Make sure we don't overwrite a "definitive" value from first phase
                            if inBounds(index) and self.object3D[index] == 1:
                                self.object3D[index] = 0 # BOUNDARY = 0
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
            print("Done one phase.")
        self.points3D = numpy.array(points3D)
        return




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
