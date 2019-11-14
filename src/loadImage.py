import bpy
import os
#from .config import IMAGES_DIR

#References:
#   https://docs.blender.org/api/blender_python_api_2_71_release/bpy.types.Image.html
#   https://blender.stackexchange.com/questions/13422/crop-image-with-python-script/13516#13516
#   https://blender.stackexchange.com/questions/3673/why-is-accessing-image-data-so-slow/3678#3678
#   https://blender.stackexchange.com/questions/15890/is-it-possible-to-edit-images-programmatically-with-the-blender-api



class loadImage:
    def __init__(self, imageFolder = "images"):
        self.imageDir = setupFilepath(imageFolder)
        self.openImages()

    def __del__(self):
        # deconstructor that removes images added by the addon
        for filename in os.listdir(self.imageDir):
            # print("filename: "+filename)
            for image in bpy.data.images:
                # print("image: "+image.name)
                if filename==image.name:
                    bpy.data.images.remove(image)
                #     print(image)
            # print(self.imageDir+filename)
            # image = bpy.data.images.load(self.imageDir+filename)
        print("Cleaned up images")

    # Blender stores images as 1D arrays, ordered as described in https://blender.stackexchange.com/questions/13422/crop-image-with-python-script/13516#13516
    # This function generates a 2D array of (r,g,b,a) tuples from said 1D list
    def blenderImageTo2D(self, blenderImage):
        print("loading image:"+blenderImage.name)
        image = []
        pixels = blenderImage.pixels[:]
        x = blenderImage.size[0]
        y = blenderImage.size[1]
        index = 0
        for i in range(x):
            pixelRow = []
            for j in range(y):
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

    # Still need to write this one. Not as urgent.
    def twoDToBlenderImage(self, image):
        return

    def createArrays(self):
        return

    def openImages(self):
        # This loops over every file in the identified images directory
        loadedImages = []
        for filename in os.listdir(self.imageDir):
            # print(self.imageDir+filename)
            image = bpy.data.images.load(self.imageDir+filename)
            loadedImages.append(self.blenderImageTo2D(image))
            # print("Loaded")
            # print(image)


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

    # scope so that the image class gets deleted
    def main():
        # Test the script itself
        image = loadImage("Sphere")
        # del image

    main()
    stopTime = time.time()
    print("Script took:",stopTime-startTime)
