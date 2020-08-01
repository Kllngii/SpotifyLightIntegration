import LIModule
from phue import Bridge
from HelperMethods import valueToHSV
class PHueModule(LIModule.LIModule):
    hueIp = None
    hueLamps = []
    bridge = None
    def __init__(self, hueLamps, hueIp = "philips-hue"):
        self.hueIp = hueIp
        self.hueLamps = hueLamps
    def setup(self):
        self.logger.info("Setup des PHue-Moduls!")
        self.bridge = Bridge(self.hueIp)
    def sendColor(self, value):
        hsv = valueToHSV(value)
        self.bridge.set_light(self.hueLamps, 'on', True, transitiontime=1)
        self.bridge.set_light(self.hueLamps, 'hue', int(hsv["h"]), transitiontime=1)
        self.bridge.set_light(self.hueLamps, 'sat', int(hsv["s"]), transitiontime=1)
        self.bridge.set_light(self.hueLamps, 'bri', int(hsv["v"]), transitiontime=1)
    def clearColor(self):
        self.bridge.set_light(self.hueLamps, 'on', False, transitiontime=1)
