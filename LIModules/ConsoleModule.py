import LIModule
import os, platform
from HelperMethods import valueToHSV, valueToRGB
class ConsoleModule(LIModule.LIModule):
    def __init__(self):
        pass
    def setup(self):
        pass
    def sendColor(self, value):
        hsv = valueToHSV(value)
        hsv["v"] = float(hsv["v"]) * (1/float(os.environ["BRIGHTNESS"]))
        hsv["h"] = float(hsv["h"]) / 65535 * 6
        if platform.system() == "Windows":
            # c | 0° | rot | 0
            # e | 60° | gelb | 1
            # a | 120° | grün | 2
            # b | 180° | cyan | 3
            # 1 | 240° | blau | 4
            # c | 360° | rot | 5
            if hsv["h"] <= 1:
                os.system('color cf')
            elif hsv["h"] <= 2:
                os.system('color ef')
            elif hsv["h"] <= 3:
                os.system('color af')
            elif hsv["h"] <= 4:
                os.system('color bf')
            elif hsv["h"] <= 5:
                os.system('color 1f')
            elif hsv["h"] <= 6:
                os.system('color cf')
        if platform.system() == "Linux":
            if hsv["h"] <= 1:
                os.system('setterm -background red -foreground white -store')
            elif hsv["h"] <= 2:
                os.system('setterm -background yellow -foreground white -store')
            elif hsv["h"] <= 3:
                os.system('setterm -background green -foreground white -store')
            elif hsv["h"] <= 4:
                os.system('setterm -background cyan -foreground white -store')
            elif hsv["h"] <= 5:
                os.system('setterm -background blue -foreground white -store')
            elif hsv["h"] <= 6:
                os.system('setterm -background magenta -foreground white -store')
        if platform.system() == "Darwin":
            rgb = valueToRGB(value)
            rgb["r"] = float(rgb["r"]) * (1/float(os.environ["BRIGHTNESS"]))
            rgb["g"] = float(rgb["g"]) * (1/float(os.environ["BRIGHTNESS"]))
            rgb["b"] = float(rgb["b"]) * (1/float(os.environ["BRIGHTNESS"]))
            os.system('osascript -e \"tell application \\"Terminal\\" to set background color of window 1 to {' + str(int(rgb['r']/255*50000)) + ', ' + str(int(rgb['g']/255*50000)) + ', ' + str(int(rgb['b']/255*50000)) + ', 0}\"')

    def clearColor(self):
        if platform.system() == "Windows":
            os.system('color 0f')
        if platform.system() == "Linux":
            os.system('setterm -background black -foreground white -store')
        if platform.system() == "Darwin":
            os.system('osascript -e \"tell application \\"Terminal\\" to set background color of window 1 to {0, 0, 0, 0}\"')
