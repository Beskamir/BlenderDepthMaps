# Script for convenient running/debugging of Blender add-ons from within Blender's text editor.
# This whole script essentially just runs __init__.py with the "DEBUG_MODE" argument passed in.
#
# Copied over from one very informative tutorial:
# "Creating multifile add-on for Blender", by Nikita from Blender - Interplanetary
# Link: https://b3d.interplanety.org/en/creating-multifile-add-on-for-blender/
# Last accessed on Nov. 23, 2019

import os
import sys

# The filesDir variable may need to be customized depending on the add-on's location on your device, as well as where you open Blender from.
 
# !!!!!!!        PLEASE DON'T REMOVE THE COMMENTED-OUT filesDir OPTIONS BELOW!        !!!!!!!
# The first time this add-on is run/installed, Blender needs to be run in administrator mode.
# That means that "../src" will not work as a path, and we have to use our custom ones.

#filesDir = "C:\\Users\\U1\\Documents\\01University\\CPSC_589\\Project\\BlenderDepthMaps\\src" #Chris2
#filesDir = "D:\\Documents\\01University\\CPSC_589\\Project\\BlenderDepthMaps\\src" #Chris
filesDir = "../src"
 
initFile = "__init__.py" 
 
if filesDir not in sys.path:
    sys.path.append(filesDir)
 
file = os.path.join(filesDir, initFile)
 
if 'DEBUG_MODE' not in sys.argv:
    sys.argv.append('DEBUG_MODE')
 
exec(compile(open(file).read(), initFile, 'exec'))
print("done")
 
if 'DEBUG_MODE' in sys.argv:
    sys.argv.remove('DEBUG_MODE')