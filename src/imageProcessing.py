import bpy
import os
#from .config import IMAGES_DIR

#References:
#   https://docs.blender.org/api/blender_python_api_2_71_release/bpy.types.Image.html
#   https://blender.stackexchange.com/questions/13422/crop-image-with-python-script/13516#13516
#   https://blender.stackexchange.com/questions/3673/why-is-accessing-image-data-so-slow/3678#3678
#   https://blender.stackexchange.com/questions/15890/is-it-possible-to-edit-images-programmatically-with-the-blender-api

#bpy.data.images.load("path\to\file.jpg")
IMAGES_DIR = "C:\\Program Files\\Blender Foundation\\Blender\\2.80\\scripts\\addons\\BlenderDepthMaps\\images"


class imageProcessor:
    def __init__(self, pathPrefix, pathSuffix, maxWidth=1024):
        self.createArrays(pathPrefix, pathSuffix, maxWidth)

    # Blender stores images as 1D arrays, ordered as described in https://blender.stackexchange.com/questions/13422/crop-image-with-python-script/13516#13516
    # This function generates a 2D array of (r,g,b,a) tuples from said 1D list
    def blenderImageToTwoD(self, blenderImage):
        image = []
        x = blenderImage.size[0]
        y = blenderImage.size[1]
        index = 0
        for i in range(x):
            pixelRow = []
            for j in range(y):
                r = blenderImage.pixels[index]
                g = blenderImage.pixels[index+1]
                b = blenderImage.pixels[index+2]
                a = blenderImage.pixels[index+3]
                pixelRow.append((r,g,b,a))
                index += 4
            # As described in https://blender.stackexchange.com/questions/13422/crop-image-with-python-script/13516#13516
            # the topmost pixel rows come latest in the image.
            # Therefore, we insert rows at the "front" of our 2D array.
            image.insert(0, pixelRow)
        return image

    # Still need to write this one. Not as urgent.
    def twoDToBlenderImage(self, image):
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
    
    def cropImages(self):
        self.images2D = []
        for i in range(6):
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
        # for i in range(6):
        #     print("~=======================")
        #     print(self.images2D[i])
            
        return
        

    def setImageHeightRanges(self):
        for i in range(6):
            self.setImageHeightRangeSingle() #EXPAND
        return
    def setImageHeightRangeSingle(self):
        # First, find the "highest" pixel's value
        # Then, find the "lowest" pixel's value ON THE OUTERMOST EDGE(S) OF THE OBJECT!
        #   (i.e. not "lowest" pixel overall, as that may correspond to indents that are invisible from other angles)
        #   ALSO, keep track of which of the four "sides" this point's "edge" will be visible from
        # Then, from ANY "side" reference image, find out where this max value occurs.
        # Then, from THE "side" reference image corresponding to the "lowest" pixel's value
        #   This is, as may be expected, the most complicated part.
        #   We will have to approach it as follows:
        #       Let A represent the image we're analyzing with this call to setImageHeightRangeSingle()
        #       Let B represent the "side" reference image we're using to try and find the lower value in A.
        #       For this example, assume A and B are "joined" on the right edge of B.
        #       Then, for each row of B, start at the rightmost side, and increment to the left.
        #       Keep track of a value "match", which is a number of pixels from the right of B's edge.
        #       Every time a pixel is darker than the one on its right, set "match" to it.
        #       Stop incrementing as soon as the pixel is lighter/"deeper" than the one on the right, and continue with the next row.
        #       IF THINGS ARE ALIGNED WELL, YOU ONLY NEED TO DO THIS FOR ONE ROW, RATHER THAN ALL OF THEM!
        #       I WILL START BY DOING IT FOR ALL OF THEM, THEN SEE HOW WELL SWITCHING TO JUST ONE WORKS!
        return

    def generate3D(self):
        return
        




if __name__ == "__main__":
    # Test function
    TEST_IMAGE_PATH_PREFIX = "lowres\\cube_"
    TEST_IMAGE_PATH_SUFFIX = ".png"
    image = imageProcessor(TEST_IMAGE_PATH_PREFIX, TEST_IMAGE_PATH_SUFFIX)
    print("Done imageProcessing.py test.")
