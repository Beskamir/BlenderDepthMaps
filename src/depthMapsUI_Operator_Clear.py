import bpy
from bpy.props import (StringProperty
                       )
from bpy.types import (
                       Operator
                       )

# Class for the button that, when clicked, clears the filename choices.
# It will also, eventually, clear the mesh that's generated from said files.
# The separator "_OT_" must appear in the name as of Blender 2.8
class WM_OT_depthMapsUI_Operator_Clear(Operator):
    bl_label = "Clear object from depth maps"
    bl_idname = "depthmaps.clear_depth_maps" # Name must have at least one "." in it to abide by Blender requirements...

    front_face_file : StringProperty(name="Filename of front depth map.")

    # Function that runs on click
    def execute(self, context):
        # Clears all of the file fields.
        context.active_object.data.depthMapAddOnProps.front_face_file = ""
        context.active_object.data.depthMapAddOnProps.left_face_file = ""
        context.active_object.data.depthMapAddOnProps.back_face_file = ""
        context.active_object.data.depthMapAddOnProps.right_face_file = ""
        context.active_object.data.depthMapAddOnProps.top_face_file = ""
        context.active_object.data.depthMapAddOnProps.bottom_face_file = ""

        return {'FINISHED'}

def register() :
    bpy.utils.register_class(WM_OT_depthMapsUI_Operator_Clear)
 
def unregister() :
    bpy.utils.unregister_class(WM_OT_depthMapsUI_Operator_Clear)