import argparse
import logging
import colorsys
from math import sin, tan
import os
parser = argparse.ArgumentParser(description='SpotifyLightIntegration')

def setupLogger():
    parser.add_argument('--debug',help='Debug-Mode aktivieren',action="store_true")
    args = parser.parse_args()
    debug = args.debug
    if not debug:
        logging.basicConfig(level='INFO')
    else:
        logging.basicConfig(level='DEBUG')
def setEnviron():
    os.environ["SPOTIPY_CLIENT_ID"] = "def1a61cd5434c3f8dd75740d2da049c"
    os.environ["SPOTIPY_CLIENT_SECRET"] = "c847178ddadc4fd59b4f1e03508a05ba"
    os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8080"
    os.environ["BRIGHTNESS"] = str(0.6)

def valueToHSV(value):
    if value == 0:
        b = {}
        b["h"] = 0
        b["s"] = 0
        b["v"] = 0
        return b
    a = {}
    a["h"] = remapValue(value)*65535
    a["s"] = 254
    a["v"] = float(os.environ["BRIGHTNESS"]) * 254
    return a

def valueToRGB(value):
    if value == 0:
        b = {}
        b["r"] = 0
        b["g"] = 0
        b["b"] = 0
        return b
    rgb = colorsys.hsv_to_rgb(remapValue(value),1, 1)
    a = {}
    a["r"] = rgb[0]*255*float(os.environ["BRIGHTNESS"])
    a["g"] = rgb[1]*255*float(os.environ["BRIGHTNESS"])
    a["b"] = rgb[2]*255*float(os.environ["BRIGHTNESS"])
    return a

def remapValue(value):
    v = tan(sin(value*80))*0.35+0.5
    if v > 1:
        v = 1
    elif v < 0:
        v = 0
    return v
