import bpy
import os
import numpy
#from .config import IMAGES_DIR

#References:
#   https://docs.blender.org/api/blender_python_api_2_71_release/bpy.types.Image.html
#   https://blender.stackexchange.com/questions/13422/crop-image-with-python-script/13516#13516
#   https://blender.stackexchange.com/questions/3673/why-is-accessing-image-data-so-slow/3678#3678
#   https://blender.stackexchange.com/questions/15890/is-it-possible-to-edit-images-programmatically-with-the-blender-api



class loadImage:
    def __init__(self):
        self.loadedImages = {}

    def __del__(self):
        # destructor that removes images added by the addon, this will keep the blend file tidy despite running the addon multiple times. 
        def cleanupImages():
            for filename in self.loadedImages:
                # print("filename: "+filename)
                for image in bpy.data.images:
                    # print("image: "+image.name)
                    if os.path.basename(filename)==image.name:
                        bpy.data.images.remove(image)
        # use the call below to disable this function if you're testing image updating
        cleanupImages()
        print("Cleaned up images")

    # Optimizations thanks to https://blender.stackexchange.com/questions/3673/why-is-accessing-image-data-so-slow/3678#3678
    # Blender stores images as 1D arrays, ordered as described in https://blender.stackexchange.com/questions/13422/crop-image-with-python-script/13516#13516
    # This function generates a 2D array of (r,g,b,a) tuples from said 1D list
    # Calling the result at index [i][j] will return the pixel in the i-th row from the bottom, j-th column from the left
    # i.e. where i=j=0 is the bottom-left pixel.
    def blendImage2xyImage(self, blenderImage):
        print("Loading image:"+blenderImage.name)
        x = blenderImage.size[0]
        y = blenderImage.size[1]
        image = numpy.empty(shape=(x,y), dtype=(float,4))
        pixels = blenderImage.pixels[:]

        index = 0
        # iterate over every row
        for i in range(y):
            # iterate over every pixel in a row
            for j in range(x):
                r = pixels[index]
                g = pixels[index+1]
                b = pixels[index+2]
                a = pixels[index+3]
                # Apparently, in blender images, lower alpha -> "darker"
                if a > 0:
                    r = r/a
                    g = g/a
                    b = b/a
                image[i][j] = (r,g,b,a)
                index += 4
        return image

    # update a given blender image with a given xyImage
    def xyImage2blendImage(self, xyImageName, xyImageContents, blendImage):
        print("Saving xyImage: "+xyImageName)
        xyPixels = []
        for row in xyImageContents:
            for pixel in row:
                (r,g,b,a) = pixel
                if a > 0:
                    r *= a
                    g *= a
                    b *= a
                xyPixels.append(r)
                xyPixels.append(g)
                xyPixels.append(b)
                xyPixels.append(a)
        blendImage.pixels[:] = xyPixels
        blendImage.update()

    def createArrays(self):
        return


    # Save the xy images to the right blend images
    def saveImages(self):
        for xyImage in self.loadedImages:
            for blendImage in bpy.data.images:
                # print("blend image image: "+blendImage.name)
                if os.path.basename(xyImage)==blendImage.name:
                    self.xyImage2blendImage(xyImage, self.loadedImages[xyImage], blendImage)

    def setupFilepath(self, imageFolder):
        # This will get the currently opened blender file's directory
        # Idea thanks to https://docs.blender.org/api/current/bpy.data.html 
        # BlendFileDir = bpy.data.filepath
        # print(BlendFileDir)
        # print(BlendFileDir.rfind('\\'))
        blendFileDir = bpy.data.filepath[:bpy.data.filepath.rfind('\\')+1]
        # print(blendFileDir) 
        blendFileDir += imageFolder + "\\"
        # print(blendFileDir) 
        return blendFileDir

    def openImage(self, imageFile):
        image = bpy.data.images.load(imageFile)
        imageResult = self.blendImage2xyImage(image)
        self.loadedImages[imageFile] = imageResult
        return imageResult

    # Open all the images in a specified folder
    def openAllImagesInFolder(self, folder):
        # This loops over every file in the identified images directory
        imageDir = self.setupFilepath(folder)
        for filename in os.listdir(imageDir):
            # print(self.imageDir+filename)
            imageFile = imageDir+filename
            image = bpy.data.images.load(imageFile)
            self.loadedImages[imageFile] = self.blendImage2xyImage(image)
            # print("Loaded")
            # print(image)
        # print(self.loadedImages[0])'''

if __name__ == "__main__":
    # Test function
    # calculate the runtime of this script
    import time
    startTime = time.time()
    print("Running script...")

    # function scope so that the image class gets deleted automatically (so the destructor will be called)
    def main():
        # Test the script itself
        image = loadImage()
        image.openAllImagesInFolder("CubeHard")
        # del image

    main()
    stopTime = time.time()
    print("Script took:",stopTime-startTime)
