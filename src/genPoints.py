import bpy
import bmesh
import numpy
from random import randint 
import time

# WIP file this likely won't run right now

# Based on voxelize.py code
def createPointCloud(vertices, name="point cloud"):
    # For now, we'll combine the voxels from each of the six views into one array and then just take the unique values.
    # Later on, this could be re-structured to, for example, render the voxels from each face in a separate colour

    print("Number of vertices:", len(vertices))
    # print("vertice data:", vertices)
    mesh = bpy.data.meshes.new("mesh")  # add a new mesh
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)  # put the object into the scene (link)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(state=True)  # select object
    mesh = obj.data
    bm = bmesh.new()

    print("Creating vertices...")
    
    printAfterCount = 100000
    nextThreshold = 0
    pointsDone = 0

    # Setup the vertices for the object  
    for vertex in vertices:
        bm.verts.new(vertex)
        pointsDone += 1
        if pointsDone > nextThreshold:
            print("Vertices completed:",pointsDone,"/",len(vertices))
            # print(pointsDone, "vertices have been added so far.")
            nextThreshold += printAfterCount
    print("Calling to_mesh().")
    bm.to_mesh(mesh)
    print("Ensuring lookup table.")
    bm.verts.ensure_lookup_table()

    debugCounter = 0
    debugSize = 50000
    # Create the faces for the object
    # for i in range(0,len(bm.verts),3):
    #     bm.faces.new( [bm.verts[i+0], bm.verts[i+1],bm.verts[i+2]])
    #     debugCounter+=1
    #     if(debugCounter%debugSize==0):
    #         print("Created triangles",debugCounter,"/",len(bm.verts)/3)

    if bpy.context.mode == 'EDIT_MESH':
        bmesh.update_edit_mesh(obj.data)
    else:
        bm.to_mesh(obj.data)
    obj.data.update()
    bm.free
    # print("Created point cloud")
    print("Created shape and merging vertices")
    # Merge overlapping vertices once everything's generated
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.object.editmode_toggle()
    print("finished merging vertices")
    return obj


def convert3DImageToPointCloud(image3D):
    vertices = []
    for x in range(len(image3D)):
        for y in range(len(image3D[x])):
            for z in range(len(image3D[x][y])):
                if(image3D[x][y][z]==0):
                    vertices.append([x,y,z])
    # Converting 3D image to point cloud
    # pointData = numpy.array(image3D)
    # createPointCloud(pointData.flatten())
    createPointCloud(vertices)
    # Finished converting 3d image to point cloud

if __name__ == "__main__":
    
    # calculate the runtime of this script
    startTime = time.time()
    # createVoxel((1,2,3))
    # Generate a 10*10*10 3D texture
    testImageArray = []
    # testImageArray = [[[-1,0], [-1, -1]], [[-1, -1], [-1, -1]]]
    print("generating data")
    # testImageArray = [
    #     [[-1, -1, -1, -1], [-1, 0, 0, -1], [-1, 0, 0, -1], [-1, 0, 0, -1]],
    #     [[-1, 0, 0, -1], [-1, 0, 0, -1], [-1, 0, 0, -1], [-1, 0, 0, -1]], 
    #     [[-1, 0, 0, -1], [-1, 0, 0, -1], [-1, 0, 0, -1], [-1, 0, 0, -1]], 
    #     [[-1, 0, 0, -1], [-1, 0, 0, -1], [-1, 0, 0, -1], [-1, -1, -1, -1]]]

    # Test functions to make sure marching cubes work
    import math
    def implicitSphere(x, y, z):
        return x*x + y*y + z*z - 1.0

    def implicitHeart(x, y, z):
        return (math.pow((2 * x*x + y*y + z*z - 1.0), 3) -
                (0.1*x*x + y*y)*z*z*z)
    xMax = 64
    yMax = 64
    zMax = 64
    debugCounter=0
    debugAmount=100000
    cellCap = (2*xMax)**3
    # for x in range(xMax):
    for x in range(-xMax,xMax):
        yArray = []
        # for y in range(yMax):
        for y in range(-yMax,yMax):
            zArray = []
            # for z in range(zMax):
            for z in range(-zMax,zMax):
                # zArray.append(0)
                # zArray.append(implicitHeart((2*x)/(xMax), (2*y)/(yMax), (2*z)/(zMax)))
                value = implicitHeart((2*x)/(xMax), (2*y)/(yMax), (2*z)/(zMax))
                # zArray.append(implicitSphere((2*x)/(xMax), (2*y)/(yMax), (2*z)/(zMax)))
                if(value<0):
                    zArray.append(-1)
                elif(value>0):
                    zArray.append(1)
                else:
                    zArray.append(0)
                # zArray.append(randint(-1,1))
                debugCounter+=1
                if(debugCounter%debugAmount==0):
                    print("genrated",debugCounter,"/",cellCap)
            yArray.append(zArray)
            # yArray.append(randint(-1,1))
        testImageArray.append(yArray)
    print("generated data")
    # print(testImageArray)
    # print(len(testImageArray))
    
    # place voxels based on that 10*10*10 array
    # imagesToMarchingInefficient(numpy.array(testImageArray))
    # efficientMarchingCubes(numpy.array(testImageArray))
    # imagesToVoxelsInefficient(testImageArray)
    # testImage = [[[0,0],[1,1]],[[1,1],[1,0]]]

    convert3DImageToPointCloud(testImageArray)

    stopTime = time.time()
    print("Script took:",stopTime-startTime)