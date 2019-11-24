# File for handling imports, reimports, and registering/unregistering of all parts of the add-on.
# Credit for the structure and explanation behind this __init__.py file goes to one very informative tutorial:
# "Creating multifile add-on for Blender", by Nikita from Blender - Interplanetary
# Link: https://b3d.interplanety.org/en/creating-multifile-add-on-for-blender/
# Last accessed on Nov. 23, 2019

bl_info = {
    "name": "Blender Depth Maps",
    "description": "Auto-generates geometry from six orthogonal depth maps",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Properties > Object Data",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}
 
# The custom modules in this application
modulesNames = [
    "depthMapsUI_PropertyGroup",
    "depthMapsUI_Operator_Generate",
    "depthMapsUI_Operator_Clear",
    "depthMapsUI_Panel", "voxelize",
    "loadImage",
    "parametrize",
    "imageProcessing",
    "controller"
    ]
 
# First, we import all of the modules we did NOT write.
import sys
import importlib
import bpy

from bpy.props import (
                       PointerProperty,
                       StringProperty
                       )
from bpy.types import (PropertyGroup)

# Then, we add the package name ("__name__") in front of the module name if we run the code as an add-on.
# If we run the code in "DEBUG_MODE", however, then __name__ is just "__main__" and not a package, so we don't append it in front as a package name.
modulesFullNames = {}
for currentModuleName in modulesNames:
    if 'DEBUG_MODE' in sys.argv:
        modulesFullNames[currentModuleName] = ('{}'.format(currentModuleName))
    else:
        modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))
 
# Blender caches imports.
# So that our most recent changes show up, reload our custom modules.
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        # If we're importing for the first time, then as the tutorial states:
        #   "importlib.import_module doesn’t create a global variable pointed to imported module."
        # So, in addition to calling import_module() for the first time, we'll need to handle the global variable ourselves.
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)
 
# Calls the "register" function present in whichever module contains it.
def register():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()

    # Get the class (extracting from the respective module using gettattr) for the depthMaps UI custom Property Group we've made.
    propertyGroupClass = getattr(sys.modules[modulesFullNames["depthMapsUI_PropertyGroup"]], "depthMapsUI_PropertyGroup")
    # Adds a "depthMappAddOnProps" property group to all NURBS surfaces.
    bpy.types.SurfaceCurve.depthMapAddOnProps = PointerProperty(type=propertyGroupClass)

# Calls the "unregister" function present in whichever module contains it.
def unregister():    
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()

    # Removes the "depthMappAddOnProps" property group to all NURBS surfaces.
    del bpy.types.SurfaceCurve.depthMapAddOnProps
 
# For debugging.
if __name__ == "__main__":
    try:
        unregister()
        print("Unregister() successful!")
    except:
        # If it fails, it's not really a big deal; we just restart Blender or ignore it.
        # So there's nothing too fancy to do here.
        print("Unregister() FAILED! Proceeding to register() step.")
    register()