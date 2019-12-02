import bpy
import bmesh
import numpy
from random import randint 
import time

# pointsToVoxels() has been modified from the function generate_blocks() in https://github.com/cagcoach/BlenderPlot/blob/master/blendplot.py
# Some changes to accomodate Blender 2.8's API changes were made, 
# and the function has been made much more efficient through creative usage of numpy.
def pointsToVoxels(points, name="VoxelMesh"):
    # For now, we'll combine the voxels from each of the six views into one array and then just take the unique values.
    # Later on, this could be re-structured to, for example, render the voxels from each face in a separate colour
    points = numpy.concatenate(tuple(points.values()))
    points = numpy.unique(points, axis=0)

    print("Number of points:", len(points))
    mesh = bpy.data.meshes.new("mesh")  # add a new mesh
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)  # put the object into the scene (link)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(state=True)  # select object
    mesh = obj.data
    bm = bmesh.new()
    #                     0          1       2         3         4         5       6        7
    block=numpy.array([ [-1,-1,-1],[-1,-1,1],[-1,1,-1],[-1,1,1],[1,-1,-1],[1,-1,1],[1,1,-1],[1,1,1] ]).astype(float)
    block*=0.5

    print("Creating vertices...")
    # Function to apply each point to each element of "block" as efficiently as possible
    # First, produce 8 copies of each point. numpy.tile() is apparently the most efficient way to do so.
    pointsTiled = numpy.tile(points, (1,8))
    # This will make each tuple 24 items long. To fix this, we need to reshape pointsTiled, and split each 24-long tuple into 8 3-longs.
    pointsDuplicated = numpy.reshape(pointsTiled, (pointsTiled.shape[0], 8, 3))
    # Then, a lambda to piecewise add the elements of "block" to a respective set of 8 duplicate points in pointsDuplicated
    blockerize = lambda x : x + block
    # Apply it
    pointsBlockerized = blockerize(pointsDuplicated)
    # pointsBlockerized is now a 2D array of thruples. Convert back to a 1D array.
    verts = numpy.reshape(pointsBlockerized, (pointsBlockerized.shape[0]*pointsBlockerized.shape[1], 3) )
    
    #print("points shape:", points.shape)
    #print("verts shape:", verts.shape)
    #print("verts:", verts)

    '''for pt in points:
        print((block+pt))
        verts=numpy.append(verts, (block+pt),axis=0)'''
    
    printAfterCount = 100000
    nextThreshold = 0
    pointsDone = 0
    #print(verts)
    for v in verts:
        bm.verts.new(v)
        pointsDone += 1
        if pointsDone > nextThreshold:
            print(pointsDone, "vertices have been added so far.")
            nextThreshold += printAfterCount
    print("Calling to_mesh().")
    bm.to_mesh(mesh)
    print("Ensuring lookup table.")
    bm.verts.ensure_lookup_table()

    nextThreshold = 0
    cubesDone = 0
    for i in range(0,len(bm.verts),8):
        bm.faces.new( [bm.verts[i+0], bm.verts[i+1],bm.verts[i+3], bm.verts[i+2]])
        bm.faces.new( [bm.verts[i+4], bm.verts[i+5],bm.verts[i+1], bm.verts[i+0]])
        bm.faces.new( [bm.verts[i+6], bm.verts[i+7],bm.verts[i+5], bm.verts[i+4]])
        bm.faces.new( [bm.verts[i+2], bm.verts[i+3],bm.verts[i+7], bm.verts[i+6]])
        bm.faces.new( [bm.verts[i+5], bm.verts[i+7],bm.verts[i+3], bm.verts[i+1]]) #top
        bm.faces.new( [bm.verts[i+0], bm.verts[i+2],bm.verts[i+6], bm.verts[i+4]]) #bottom
        cubesDone += 1
        if cubesDone > nextThreshold:
            print(cubesDone, "cubes have been made so far.")
            nextThreshold += printAfterCount
    if bpy.context.mode == 'EDIT_MESH':
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
    obj.data.update()
    bm.free
    return obj

# Given a 3D array of 0 and 1's it'll place a voxel in every cell that has a 1 in it
def imagesToVoxelsInefficient(image3D):
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
    imagesToVoxelsInefficient(testImageArray)
    # testImage = [[[0,0],[1,1]],[[1,1],[1,0]]]
    
    stopTime = time.time()
    print("Script took:",stopTime-startTime)