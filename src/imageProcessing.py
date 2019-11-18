import bpy
import os
import numpy
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
    def __init__(self, pathPrefix, pathSuffix, maxWidth=1024):
        self.createArrays(pathPrefix, pathSuffix, maxWidth)

    # Blender stores images as 1D arrays, ordered as described in https://blender.stackexchange.com/questions/13422/crop-image-with-python-script/13516#13516
    # This function generates a 2D array of (r,g,b,a) tuples from said 1D list
    # Calling the result at index [i][j] will return the pixel in the i-th row, j-th column, where i=j=0 is the top-left pixel.
    def blenderImageToTwoD(self, blenderImage):
        x = blenderImage.size[0]
        y = blenderImage.size[1]
        image = numpy.empty(shape=(x,y), dtype=(float,4))
        index = 0
        for i in range(x):
            pixelRow = []
            for j in range(y):
                r = blenderImage.pixels[index]
                g = blenderImage.pixels[index+1]
                b = blenderImage.pixels[index+2]
                a = blenderImage.pixels[index+3]
                pixelRow[i][j] = (r,g,b,a)
                index += 4
            # As described in https://blender.stackexchange.com/questions/13422/crop-image-with-python-script/13516#13516
            # the topmost pixel rows come latest in the image.
            # Therefore, we insert rows at the "front" of our 2D array.
        return image

    # Still need to write this one. Not as urgent.
    def twoDToBlenderImage(self, image):
        print("NOT IMPLEMENTED YET!")
        raise NotImplementedError
        return

    def createArrays(self, pathPrefix, pathSuffix, maxWidth=1024):
        self.pathPrefix = pathPrefix
        self.pathSuffix = pathSuffix
        self.maxWidth = maxWidth
        
        self.cropImages()

        #self.resizeImages()
        #self.alignImages()

        self.setImageHeightRanges()
        self.generate3D()
        print("3D map generated!")
        return
    
    def cropImages(self):
        self.images2D = []
        for i in FACES:
            # Load the image
            filename = os.path.join(IMAGES_DIR, self.pathPrefix + str(i) + self.pathSuffix)
            print("Loading:",filename)
            image = self.blenderImageToTwoD(bpy.data.images.load(filename))
            
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
            cropTop = 0
            foundPosAlpha = False
            while not foundPosAlpha:
                for j in range(len(image[0])):
                    if image[cropTop][j][3] > 0.0:
                        foundPosAlpha = True
                        break
                if foundPosAlpha:
                    break
                else:
                    cropTop += 1
            # BOTTOM
            cropBottom = len(image)-1
            foundPosAlpha = False
            while not foundPosAlpha:
                for j in range(len(image[0])):
                    if image[cropBottom][j][3] > 0.0:
                        foundPosAlpha = True
                        break
                if foundPosAlpha:
                    break
                else:
                    cropBottom -= 1
            image = [image[i][cropLeft:cropRight+1] for i in range(cropTop,cropBottom+1)] 
            self.images2D.append(image)
            print(i, "---------------------")
            print("cropLeft:", cropLeft)
            print("cropRight:", cropRight)
            print("cropTop:", cropTop)
            print("cropBottom:", cropBottom)
        self.xLen = len(self.images2D[TOP_FACE])
        self.yLen = len(self.images2D[FRONT_FACE][0])
        self.zLen = len(self.images2D[FRONT_FACE])

        return
        

    def setImageHeightRanges(self):
        self.depthDictionary = {}
        for i in FACES:
            self.setImageHeightRangeSingle(i)
        return
    
    def setImageHeightRangeSingle(self, selectedFace):
        selectedImage = self.images2D[selectedFace]
        # First, find the "highest" pixel's value
        highest = 0.0
        for i in range(len(selectedImage)):
            for j in range(len(selectedImage[i])):
                # Check the pixel's alpha, to ensure pixel is not transparent.
                if selectedImage[i][j][3] > 0:
                    # Choose any of the RGB channels for height comparison
                    if selectedImage[i][j][0] > highest:
                        highest = selectedImage[i][j][0]
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
            if correspondingSide == BOTTOM_SIDE:
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
            while selectedImage[row][leftColumn][3] <= 0 and leftColumn < len(selectedImage[row]):
                leftColumn += 1
            rightColumn = len(selectedImage[row]) - 1
            while selectedImage[row][rightColumn][3] <= 0 and rightColumn >= 0:
                rightColumn -= 1
            if leftColumn < len(selectedImage[row]) and selectedImage[row][leftColumn][0] < lowestEdge:
                lowestEdge = selectedImage[row][leftColumn][0]
                lowestSide = LEFT_SIDE
            if rightColumn >= 0 and selectedImage[row][rightColumn][0] < lowestEdge:
                lowestEdge = selectedImage[row][rightColumn][0]
                lowestSide = RIGHT_SIDE
        # Then, the top and bottom sides are tested.
        # (We also do checks on indices in case we somehow, in spite of prior cropping, end up with an all-transparent column)
        for column in range(len(selectedImage[0])):
            #Test from the top
            topRow = 0
            while selectedImage[topRow][column][3] <= 0 and topRow < len(selectedImage):
                topRow += 1
            bottomRow = len(selectedImage) - 1
            while selectedImage[bottomRow][column][3] <= 0 and bottomRow >= 0:
                bottomRow -= 1
            if topRow < len(selectedImage) and selectedImage[topRow][column][0] < lowestEdge:
                lowestEdge = selectedImage[topRow][column][0]
                lowestSide = TOP_SIDE
            if bottomRow >= 0 and selectedImage[bottomRow][column][0] < lowestEdge:
                lowestEdge = selectedImage[bottomRow][column][0]
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
            startIndex = 0
            colIncrement = 1
            if correspondingSide == RIGHT_SIDE:
                startIndex = len(correspondingFaceImage[0])-1
                colIncrement = -1
            columnToSearch = startIndex + colIncrement # Start 1 from the edge
            # This array will keep track of the max height found in each row, and where it is.
            rowMaxes = [ { "val": 0.0, "depth":startIndex } ] * len(correspondingFaceImage)
            # Search column-by-column until we find something opaque.
            while columnToSearch in range (len(correspondingFaceImage[0])):
                for row in range(len(correspondingFaceImage)):
                    # Alpha check & comparing with current max
                    if correspondingFaceImage[row][columnToSearch][3] > 0.0 and correspondingFaceImage[row][columnToSearch][0] > rowMaxes[row]["val"]:
                        rowMaxes[row]["val"] = correspondingFaceImage[row][columnToSearch][0]
                        rowMaxes[row]["depth"] = columnToSearch
                columnToSearch += colIncrement
            # Now, we set depthInwardsLowest to be the greatest distance from the edge observed in rowMaxes.
            for r in rowMaxes:
                curDist = abs(r["depth"] - startIndex)
                if curDist > depthInwardsLowest:
                    depthInwardsLowest = curDist
        # THEN, we handle the case for when correspondingSide is TOP or BOTTOM
        else:
            startIndex = 0
            rowIncrement = 1
            if correspondingSide == BOTTOM_SIDE:
                startIndex = len(correspondingFaceImage)-1
                rowIncrement = -1
            rowToSearch = startIndex + rowIncrement # Start 1 from the edge
            # This array will keep track of the max height found in each column, and where it is.
            colMaxes = [ { "val": 0.0, "depth":startIndex } ] * len(correspondingFaceImage[0])
            # Search row-by-row until we find something opaque.
            while rowToSearch in range (len(correspondingFaceImage)):
                for col in range(len(correspondingFaceImage[0])):
                    # Alpha check & comparing with current max
                    if correspondingFaceImage[rowToSearch][col][3] > 0.0 and correspondingFaceImage[rowToSearch][col][0] > colMaxes[col]["val"]:
                        colMaxes[col]["val"] = correspondingFaceImage[rowToSearch][col][0]
                        colMaxes[col]["depth"] = rowToSearch
                rowToSearch += rowIncrement
            # Now, we set depthInwardsLowest to be the greatest distance from the edge observed in colMaxes.
            for c in colMaxes:
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

        self.object3D = numpy.ones(shape=(xLen,yLen,zLen)) # Fill with inside value (1)

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
                print("REMINDER: ALLOW USER-INPUT MODIFICATION FOR CASE WHERE DEPTH RANGE MAPPING CANNOT BE AUTOMATICALLY DETERMINED!")
                print("SETTING ALL VALUES TO 'MAX' AS TEMPORARY DEFAULT!")
                # The actual logic happens deeper inside the while loop. Look for it below, marked with "#updateme"
            index = startDict[face] # Convert into list so that it's mutable
            # We'll do two phases.
            # First, we'll do all "definitive" cells, with alpha values zero or one.
            # Then, we'll do all partial-alpha cells IF there's no conflict.
            for phase in range(2):
                while inBounds(index):
                    refIndexHoriz = index # Save current index before the "vert" and "inwards" coords are altered
                    while inBounds(index):
                        refIndexVert = index # Save current index before the "inwards" coord is altered
                        depth = 0
                        index2D = (pixelXIndex, pixelYIndex)
                        pixelVal = self.images2D[face][index2D]
                        if depthRange == 0:
                            #updateme
                            depthCap = highestCellDepth
                        else:
                            depthCap = ((highestFloat-pixelVal[0])*lowestEdgeCellDepth + (pixelVal[0] - lowestEdgeFloat)*highestCellDepth)/depthRange
                        # Alpha check
                        if pixelVal[3] == 1 and phase == 0:
                            while inBounds(index) and depth < depthCap:
                                self.object3D[index] = -1 # OUTSIDE = -1
                                index = add(index, iteration3D_Dictionary[face]["inwards"])
                                depth += 1
                            if inBounds(index) and self.object3D[index] == 1:
                                self.object3D[index] = 0 # BOUNDARY = 0
                        elif pixelVal[3] == 0 and phase == 0:
                            while inBounds(index):
                                self.object3D[index] = -1 # OUTSIDE = -1
                                index = add(index, iteration3D_Dictionary[face]["inwards"])
                        elif pixelVal[3] != 0 and pixelVal[3] != 1 and phase == 1:
                            while inBounds(index) and depth < depthCap:
                                # Make sure we don't overwrite a "definitive" value from first phase
                                if self.object3D[index] == 1:
                                    self.object3D[index] = -1 # OUTSIDE = -1
                                index = add(index, iteration3D_Dictionary[face]["inwards"])
                                depth += 1
                            # Make sure we don't overwrite a "definitive" value from first phase
                            if inBounds(index) and self.object3D[index] == 1:
                                self.object3D[index] = 0 # BOUNDARY = 0
                        # reset "inwards" and increment "vert"
                        index = add(refIndexVert, iteration3D_Dictionary[face]["vertical"])
                        pixelYIndex += 1
                    # reset "vert" and "inwards" and increment "horiz"
                    index = add(refIndexHoriz, iteration3D_Dictionary[face]["horizontal"])
                    pixelXIndex += 1
        return




if __name__ == "__main__":
    # Test function
    TEST_IMAGE_PATH_PREFIX = "lowres\\cube_"
    TEST_IMAGE_PATH_SUFFIX = ".png"
    image = imageProcessor(TEST_IMAGE_PATH_PREFIX, TEST_IMAGE_PATH_SUFFIX)
    print("Done imageProcessing.py test.")
