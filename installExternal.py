 
# First, we import all of the modules we did NOT write.
import sys
import subprocess
import importlib
from pathlib import Path

print("""
===================================
INSTALLING THIRD-PARTY LIBRARIES!
===================================
""")

# Keys = the library name, i.e. the one for installation
# Values = the module name, i.e. the one used for importing 
externalLibs = {"scikit-image": "skimage", "scipy": "scipy"}


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
