import bpy
from bpy.props import (StringProperty
                       )
from bpy.types import (
                       Operator
                       )

import imageProcessing

# Class for the button that, when clicked, calls the functions needed to generate the mesh.
# The separator "_OT_" must appear in the name as of Blender 2.8
class WM_OT_depthMapsUI_Operator_Generate(Operator):
    bl_label = "Generate object from depth maps"
    bl_idname = "depthmaps.run_depth_maps" # Name must have at least one "." in it to abide by Blender requirements...

    front_face_file : StringProperty(name="Filename of front depth map.")

    # Function that runs on click
    def execute(self, context):
        imgp = imageProcessing.imageProcessor("Makuta", "Takanuva")
        imgp.testPrint()
        #print("\n~\nACTIVE OBJECT TYPE:\n",bpy.context.active_object.type, end="\n~\n\n")

        return {'FINISHED'}

def register() :
    bpy.utils.register_class(WM_OT_depthMapsUI_Operator_Generate)
 
def unregister() :
    bpy.utils.unregister_class(WM_OT_depthMapsUI_Operator_Generate)