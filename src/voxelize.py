import bpy
from random import randint 
import time

# Given a 3D array of 0 and 1's it'll place a voxel in every cell that has a 1 in it
def imagesToVoxels(image3D):
    for xValue in range(len(image3D)):
        for yValue in range(len(image3D[xValue])):
            for zValue in range(len(image3D[xValue][yValue])):
                if(image3D[xValue][yValue][zValue]==0):
                    createVoxel((xValue,yValue,zValue))

# place a voxel at a given position, using mesh.primitive_cube_add is really slow so it might be worth making this faster 
def createVoxel(position):
    bpy.ops.mesh.primitive_cube_add(location=position,size=1)
    # print(position)
    
if __name__ == "__main__":
    
    # calculate the runtime of this script
    startTime = time.time()

    # createVoxel((1,2,3))
    # Generate a 10*10*10 3D texture
    testImageArray = []
    for x in range(10):
        yArray = []
        for y in range(10):
            zArray = []
            for z in range(10):
                zArray.append(0)
                # zArray.append(randint(0,1))
            yArray.append(zArray)
        testImageArray.append(yArray)

    # print(testImageArray)
    # place voxels based on that 10*10*10 array
    imagesToVoxels(testImageArray)
    # testImage = [[[0,0],[1,1]],[[1,1],[1,0]]]
    
    stopTime = time.time()
    print("Script took:",stopTime-startTime)