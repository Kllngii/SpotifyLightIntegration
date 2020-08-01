import logging
from HelperMethods import setupLogger, setEnviron
from LIModules.MQTTModule import MQTTModule as MQTTModule
from LIModules.PHueModule import PHueModule as PHueModule
from LIModules.ConsoleModule import ConsoleModule as ConsoleModule
from SpotifyHandler import SpotifyHandler
import os
from time import sleep

import random

liModules = []
logger = logging.getLogger('SpotifyLightIntegration')
spotify = None

def setup():
    setupLogger()
    setEnviron()
    liModules.append(MQTTModule())
    liModules.append(PHueModule(hueLamps=[4,5]))
    liModules.append(ConsoleModule())
    global spotify
    spotify = SpotifyHandler("lasee123", liModules)
    spotify.setup()
    for m in liModules:
        m.setup()

def loop():
    spotify.loop()
def clear():
    for m in liModules:
        m.clearColor()
try:
    setup()
    loop()
except KeyboardInterrupt:
    logger.info("Beende - KeyboardInterrupt")
    clear()
