import bpy

from bpy.types import (Panel
                       )

# "_PT_" separator in class name is required as of Blender 2.8
class OBJECT_PT_depthMapsUI_Panel(Panel):
    bl_label = "Blender Depth Map Options"
    bl_idname = "OBJECT_PT_depth_maps_panel"
    # Panel will appear under Properties > Data view for surfaces.
    bl_space_type = "PROPERTIES"   
    bl_region_type = "WINDOW"
    bl_context = "data"    
    

    @classmethod
    def poll(self,context):
        # For now, only display this panel if an object is selected and is a NURBS surface.
        return context.object is not None and context.active_object.type == "SURFACE"

    def draw(self, context):
        layout = self.layout
        
        propsToSet = layout.operator("depthmaps.run_depth_maps") # The button to generate the shape
        
        currentProps = context.active_object.data.depthMapAddOnProps
        layout.prop(currentProps, "front_face_file", text="Front depth map file:")

        allEmpty = True
        for face in ["front", "left", "back", "right", "top", "bottom"]:
            if len(currentProps.get(face+"_face_file", "")) > 0:
                allEmpty = False
        # If the front depth map is 
        if not allEmpty: # currentProps.front_face_file != None and currentProps.front_face_file != "":
            #layout.label(text="Below fields have been initially populated with guesses from the front face's file when possible.")
            layout.prop(currentProps, "left_face_file", text="Left depth map file:")
            layout.prop(currentProps, "back_face_file", text="Back depth map file:")
            layout.prop(currentProps, "right_face_file", text="Right depth map file:")
            layout.prop(currentProps, "top_face_file", text="Top depth map file:")
            layout.prop(currentProps, "bottom_face_file", text="Bottom depth map file:")

        layout.operator("depthmaps.clear_depth_maps")
        propsToSet.front_face_file = currentProps.front_face_file
        propsToSet.left_face_file = currentProps.left_face_file
        propsToSet.back_face_file = currentProps.back_face_file
        propsToSet.right_face_file = currentProps.right_face_file
        propsToSet.top_face_file = currentProps.top_face_file
        propsToSet.bottom_face_file = currentProps.bottom_face_file
        
        '''print("\n\nPROPS:")
        for attr in dir(context.active_object.data):
            if hasattr( context.active_object.data, attr ):
                print( "obj.%s = %s" % (attr, getattr(context.active_object.data, attr)))'''

        layout.separator()
        
# Register the panel with Blender
def register() :
    bpy.utils.register_class(OBJECT_PT_depthMapsUI_Panel)
    
def unregister() :
    bpy.utils.unregister_class(OBJECT_PT_depthMapsUI_Panel)