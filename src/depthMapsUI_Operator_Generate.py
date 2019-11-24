import bpy
from bpy.props import (StringProperty
                       )
from bpy.types import (
                       Operator
                       )

import imageProcessing
from voxelize import pointsToVoxels

# Class for the button that, when clicked, calls the functions needed to generate the mesh.
# The separator "_OT_" must appear in the name as of Blender 2.8
class WM_OT_depthMapsUI_Operator_Generate(Operator):
    bl_label = "Generate object from depth maps"
    bl_idname = "depthmaps.run_depth_maps" # Name must have at least one "." in it to abide by Blender requirements...

    front_face_file : StringProperty(name="Filename of front depth map.")
    left_face_file : StringProperty(name="Filename of left depth map.")
    back_face_file : StringProperty(name="Filename of back depth map.")
    right_face_file : StringProperty(name="Filename of right depth map.")
    top_face_file : StringProperty(name="Filename of top depth map.")
    bottom_face_file : StringProperty(name="Filename of bottom depth map.")

    # Function that runs on click
    def execute(self, context):
        files = []
        for face in ["front", "left", "back", "right", "top", "bottom"]:
            files.append(getattr(self, face+"_face_file"))
        print("FILES:", files)
        imgp = imageProcessing.imageProcessor(files)
        pointsToVoxels(imgp.points3D)
        #print("\n~\nACTIVE OBJECT TYPE:\n",bpy.context.active_object.type, end="\n~\n\n")

        return {'FINISHED'}

def register() :
    bpy.utils.register_class(WM_OT_depthMapsUI_Operator_Generate)
 
def unregister() :
    bpy.utils.unregister_class(WM_OT_depthMapsUI_Operator_Generate)