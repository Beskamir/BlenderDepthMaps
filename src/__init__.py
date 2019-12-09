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

externalLibs = {"scikit-image": "skimage", "scipy":"scipy"}
 
# First, we import all of the modules we did NOT write.
import sys
import subprocess
import importlib
import bpy
from pathlib import Path


from bpy.props import (
                       PointerProperty,
                       StringProperty
                       )
from bpy.types import (PropertyGroup)

print("""
===================================
INITIALIZING!
===================================
""")

# Code for installing third-party modules not packed with Blender was modified slightly from:
# "How to write my add-on so that when installed it also installs dependencies (let's say: scipy or numpy-quaternion)?"
# asked by user gmagno on blender.stackexchange.com.
# The answer referenced was written by user Zollie.
# Link: https://blender.stackexchange.com/a/153520
# Date accessed: Dec. 6, 2019

# OS independent (Windows: bin\python.exe; Mac/Linux: bin/python3.7m)
py_path = Path(sys.prefix) / "bin"
# first file that starts with "python" in "bin" dir
py_exec = next(py_path.glob("python*"))
# ensure pip is installed & update
subprocess.call([str(py_exec), "-m", "ensurepip"])
subprocess.call([str(py_exec), "-m", "pip", "install", "--upgrade", "pip"])
# install dependencies using pip
# dependencies such as 'numpy' could be added to the end of this command's list
for lib in externalLibs.keys():
    try:
        testModule = importlib.import_module(externalLibs[lib], package=None)
        print("\nModule", externalLibs[lib], "already installed!\n")
    except ImportError as e:
        print("\nModule", externalLibs[lib], "NOT already installed!\n")
        print("PY_EXEC:", py_exec)
        subprocess.call([str(py_exec),"-m", "pip", "install", "--user", lib])

print("\n~~~ INSTALLATION TROUBLESHOOTING ~~~")
print("Third-Party Module Installation is Finished Running!")
print("If you find the libraries did not install because of a 'Permission Error', try restarting Blender as an Administrator and run this again.")
print("Additionally, if a library has been installed for the first time, you may need to re-start Blender for it to work.")
print("Otherwise, you'll get an error when trying to import the module!")
print("This is slightly annoying, but it only has to be done once; after everything works, you can always just use Blender as normal, like you used to!")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")



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
        print("Unregister() FAILED, but this is probably NOT AN ISSUE!")
        print("Proceeding to register() step.")
    register()