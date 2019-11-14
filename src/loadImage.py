import bpy
import os
#from .config import IMAGES_DIR

#References:
#   https://docs.blender.org/api/blender_python_api_2_71_release/bpy.types.Image.html
#   https://blender.stackexchange.com/questions/13422/crop-image-with-python-script/13516#13516
#   https://blender.stackexchange.com/questions/3673/why-is-accessing-image-data-so-slow/3678#3678
#   https://blender.stackexchange.com/questions/15890/is-it-possible-to-edit-images-programmatically-with-the-blender-api



class loadImage:
    loadedImages = []
    def __init__(self, imageFolder = "images"):
        # constructor that loads images from a specified folder
        self.imageDir = setupFilepath(imageFolder)
        self.openImages()
        self.saveImages()

    def __del__(self):
        # destructor that removes images added by the addon, this will keep the blend file tidy despite running the addon multiple times. 
        def cleanupImages():
            for filename in os.listdir(self.imageDir):
                # print("filename: "+filename)
                for image in bpy.data.images:
                    # print("image: "+image.name)
                    if filename==image.name:
                        bpy.data.images.remove(image)
        # use the call below to disable this function if you're testing image updating
        cleanupImages()
        print("Cleaned up images")

    # Optimizations thanks to https://blender.stackexchange.com/questions/3673/why-is-accessing-image-data-so-slow/3678#3678
    # Blender stores images as 1D arrays, ordered as described in https://blender.stackexchange.com/questions/13422/crop-image-with-python-script/13516#13516
    # This function generates a 2D array of (r,g,b,a) tuples from said 1D list
    def blendImage2xyImage(self, blenderImage):
        print("Loading image:"+blenderImage.name)
        image = []
        pixels = blenderImage.pixels[:]
        x = blenderImage.size[0]
        y = blenderImage.size[1]
        index = 0
        # iterate over every row
        for i in range(y):
            pixelRow = []
            # iterate over every pixel in a row
            for j in range(x):
                r = pixels[index]
                g = pixels[index+1]
                b = pixels[index+2]
                a = pixels[index+3]
                pixelRow.append((r,g,b,a))
                index += 4
            # As described in https://blender.stackexchange.com/questions/13422/crop-image-with-python-script/13516#13516
            # the topmost pixel rows come latest in the image.
            # Therefore, we insert rows at the "front" of our 2D array.
            image.insert(0, pixelRow)
        # print(image)
        return image

    # update a given blender image with a given xyImage
    def xyImage2blendImage(self, xyImage, blendImage):
        print("Saving xyImage: "+xyImage[0])
        xyPixels = []
        # Reversed to fix the thing that's done in blendImage2xyImage
        for row in reversed(xyImage[1]):
            for pixel in row:
                for i in range(4):
                    xyPixels.append(pixel[i])
        blendImage.pixels[:] = xyPixels
        blendImage.update()

    def createArrays(self):
        return

    # Open all the images in a specified folder
    def openImages(self):
        # This loops over every file in the identified images directory
        for filename in os.listdir(self.imageDir):
            # print(self.imageDir+filename)
            image = bpy.data.images.load(self.imageDir+filename)
            self.loadedImages.append((filename,self.blendImage2xyImage(image)))
            # print("Loaded")
            # print(image)
        # print(self.loadedImages[0])

    # Save the xy images to the right blend images
    def saveImages(self):
        for xyImage in self.loadedImages:
            for blendImage in bpy.data.images:
                # print("blend image image: "+blendImage.name)
                if xyImage[0]==blendImage.name:
                    self.xyImage2blendImage(xyImage, blendImage)

def setupFilepath(imageFolder):
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

if __name__ == "__main__":
    # Test function
    # calculate the runtime of this script
    import time
    startTime = time.time()
    print("Running script...")

    # function scope so that the image class gets deleted automatically (so the destructor will be called)
    def main():
        # Test the script itself
        image = loadImage("CubeHard")
        # del image

    main()
    stopTime = time.time()
    print("Script took:",stopTime-startTime)
