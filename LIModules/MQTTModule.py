import LIModule
import paho.mqtt.client as mqtt
from HelperMethods import valueToRGB

class MQTTModule(LIModule.LIModule):
    mqttIp = None
    mqttClient = None
    mqttPort = None

    def __init__(self, mqttIp = "localhost", mqttPort = 1883):
        self.mqttIp = mqttIp
        self.mqttPort = mqttPort

    def setup(self):
        self.logger.info("Setup des MQTT-Moduls!")
        self.mqttClient = mqtt.Client()
        self.mqttClient.connect(self.mqttIp, self.mqttPort, 5)

    def sendColor(self, value):
        rgb = valueToRGB(value)
        self.mqttClient.publish("color", "{\"color\":" + str(rgb).replace("\'", "\"") + "}")

    def clearColor(self):
        self.mqttClient.publish("color", "{\"color\":" + str({"r":0,"g":0,"b":0}).replace("\'", "\"") + "}")
