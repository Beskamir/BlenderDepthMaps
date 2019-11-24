# Script for convenient running/debugging of Blender add-ons from within Blender's text editor.
# This whole script essentially just runs __init__.py with the "DEBUG_MODE" argument passed in.
#
# Copied over from one very informative tutorial:
# "Creating multifile add-on for Blender", by Nikita from Blender - Interplanetary
# Link: https://b3d.interplanety.org/en/creating-multifile-add-on-for-blender/
# Last accessed on Nov. 23, 2019

import os
import sys
 
# This field needs to be customized depending on the add-on's location on your device
filesDir = "C:/Program Files/Blender Foundation/Blender/2.80/scripts/addons/BlenderDepthMaps/src"
 
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