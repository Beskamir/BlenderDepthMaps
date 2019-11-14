import bpy
import os
#from .config import IMAGES_DIR

class Controller():
    def __init__(self):
        pass

if __name__ == "__main__":
    # Test function
    # calculate the runtime of this script
    import time
    startTime = time.time()
    print("Running script...")

    # function scope so that the image class gets deleted automatically (so the destructor will be called)
    def main():
        # Test the script itself
        # Controller("CubeHard")
        Controller()
        # del image

    main()
    stopTime = time.time()
    print("Script took:",stopTime-startTime)
