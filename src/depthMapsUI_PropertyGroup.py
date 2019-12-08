import bpy

from bpy.props import (StringProperty,
                        IntProperty,
                        EnumProperty
                       )
from bpy.types import (
                       PropertyGroup,
                       PointerProperty
                       )

import re # For guessing filenames for the other files.

# For testing if files exist
import os.path
from os import path


class depthMapsUI_PropertyGroup(PropertyGroup):

    def frontFaceGetter(self):
        return self.get("front_face_file", "")

    def frontFaceSetter(self, value):
        # Record the previous value
        oldValue = self.get("front_face_file", "")

        # Set the new front_face_file value
        self["front_face_file"] = value

        # Check if the other values have been set yet
        othersSet = False
        for face in ["left", "back", "right", "top", "bottom"]:
            if len( self.get(face + "_face_file", "")) > 0:
                othersSet = True
                break

        # If the old value was "" or None, but the new one is not, OR all of the other sides' values are still blank,
        # then we add new guesses for the other five image file names.
        if (not othersSet) or ((oldValue == None or oldValue == "") and (value != None and value != "")):
            # Naming conventions a user might use
            lowercaseOptions = ["front", "left", "back", "right", "top", "bottom"]
            uppercaseOptions = ["Front", "Left", "Back", "Right", "Top", "Bottom"]
            allCapsOptions = ["FRONT", "LEFT", "BACK", "RIGHT", "TOP", "BOTTOM"]
            numberOptions = ["0", "1", "2", "3", "4", "5"]

            options = [lowercaseOptions, uppercaseOptions, allCapsOptions, numberOptions]

      
            # Try matching each of these naming conventions against the front face's file and see if we get a match
            for option in options:
                # Pattern ensures that our "front"/"0"/etc. string appears in the file name, not in a proceeding directory name
                # A more sophisticated search would also handle cases for which option[0] appears multiple times in the file's name,
                # but time should be devoted to more important tasks at the moment.
                pattern = r"^(?P<prefix>.*)" + re.escape(option[0]) + r"(?P<suffix>[^\\/]+)$"
                filenameMatch = re.match(pattern, value, flags=re.DOTALL)
                # If we get a match, we generate our guesses
                if filenameMatch != None:
                    prefixToSearch = prefix = filenameMatch.group("prefix")
                    if prefix[0:2] == "//":
                        prefixToSearch = "./" + prefix[2:]
                    suffix = filenameMatch.group("suffix")
                    guess = []
                    allGuessesExist = True
                    for i in range(5):
                        guess.append(prefix + option[i+1] + suffix)
                        guessToSearch = prefixToSearch + option[i+1] + suffix
                        if not path.exists(guessToSearch):
                            allGuessesExist = False

                    # If all of the guesses are valid, then we update the other file names with them
                    if allGuessesExist:
                        self.left_face_file = guess[0]
                        self.back_face_file = guess[1]
                        self.right_face_file = guess[2]
                        self.top_face_file = guess[3]
                        self.bottom_face_file = guess[4]
                        break

        
    # Stores the filename for the front depth map
    front_face_file : StringProperty(
        name="Front depth map file",
        description="Path to file for front depth map",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
        # Getter and Setter needed to record old value before setting new one.
        get=frontFaceGetter,
        set=frontFaceSetter
    )
    left_face_file : StringProperty(
        name="Left depth map file",
        description="Path to file for left depth map",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')
    back_face_file : StringProperty(
        name="Back depth map file",
        description="Path to file for back depth map",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')
    right_face_file : StringProperty(
        name="Right depth map file",
        description="Path to file for right depth map",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')
    top_face_file : StringProperty(
        name="Top depth map file",
        description="Path to file for top depth map",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')
    bottom_face_file : StringProperty(
        name="Bottom depth map file",
        description="Path to file for bottom depth map",
        default="",
        maxlen=1024,
        subtype='FILE_PATH')
    max_width : IntProperty(
        name="Max width along any axis.",
        description="Sets a constraint on the size of the generated voxel object.",
        default=1024
    )
    mesh_mode : EnumProperty(
        items=[
            ('voxelsMode', 'Voxels', 'Voxels mode', '', 0),
            ('marchingMode', 'Marching Cubes', 'Marching cubes mode', '', 1)
            # ('60', '60', '60', '', 2),
            # ('90', '90', '90', '', 3),
            # ('120', '120', '120', '', 4),
        ],
        default='marchingMode'
    )



    


# Register the property group with Blender
def register() :
    bpy.utils.register_class(depthMapsUI_PropertyGroup)
    
def unregister() :
    bpy.utils.unregister_class(depthMapsUI_PropertyGroup)
