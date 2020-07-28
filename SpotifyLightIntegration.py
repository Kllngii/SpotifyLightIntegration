import os
import sys
import logging
import sched
import time
import colorsys
import platform
from math import sin, tan
from datetime import datetime

import spotipy
import spotipy.util as util
import paho.mqtt.client as mqtt
from phue import Bridge
from spotipy.oauth2 import SpotifyClientCredentials

### FR und Bugfix:
# FR: https://github.com/ggravlingen/pytradfri Trådfri Integration
# FR: https://docs.python.org/3/library/configparser.html Config Datei mit Nutzerdaten
# FR: GUI für die Anwendungswerte und Nutzerwerte
# FR: Hue Farbe vor Start merken und am Ende wiederherstellen

### Nutzerwerte
username = 'username'
mqttIp = 'localhost'
bridgeIp = 'philips-hue'
hueLamps = [] #Fill with lamp-ids e. g: [4,5]

### Anwendungswerte
mqttEnabled = True
bridgeEnabled = True
consoleEnabled = True
debug = False
filter = 0.0
offset = 200
hueOffset = -0
cooldown = 100
brightness = 1.0 * 254

### Variablen
logger = logging.getLogger('SpotifyLightIntegration')
mqttClient = None
bridge = None
songID = ''
delay = 2

def mqttSetup():
    global mqttClient
    mqttClient = mqtt.Client()
    mqttClient.connect(mqttIp, 1883, 5)

def getCurrentTrack(token, sc):
    try:
        sp = spotipy.Spotify(auth=token)
        track = sp.current_user_playing_track()
        trackId = str(track["item"]["id"])
        features = sp.audio_features(trackId)
        tempo = features[0]["tempo"]/60
        analysis = sp.audio_analysis(trackId)

        logger.debug(trackId)

        segmentStart = {}
        segmentDuration = {}
        segmentConfidence = {}
        segmentLoudnessStart = {}
        segmentLoudnessMax = {}
        segmentLoudnessMaxTime = {}
        segmentLoudnessDifferenceStartMax = {}
        segmentLoudnessSlope = {}

        segmentStartIntervall = {}
        segmentDurationIntervall = {}
        segmentConfidenceIntervall = {}
        segmentLoudnessSlopeIntervall = {}
        segmentLoudnessMaxIntervall = {}

        i = 0;

        for segment in analysis["segments"]:
            segmentStart[i] = segment["start"]
            segmentDuration[i] = segment["duration"]
            segmentConfidence[i] = segment["confidence"]
            segmentLoudnessStart[i] = segment["loudness_start"]
            segmentLoudnessMax[i] = segment["loudness_max"]
            segmentLoudnessMaxTime[i] = ((segment["loudness_max_time"]) * 1000) + 1
            segmentLoudnessDifferenceStartMax[i] = abs(segmentLoudnessStart[i]) - abs(segmentLoudnessMax[i])
            segmentLoudnessSlope[i] = (segmentLoudnessDifferenceStartMax[i] / segmentLoudnessMaxTime[i]) * 2
            i = i + 1

        segmentStartTimeFirst = 0
        segmentStartTimeLast = 0
        for i in range(0, len(segmentStart)):
            if segmentStart[i] > ((track["progress_ms"] - 3000) / 1000):
                segmentStartTimeFirst = i
                break

        for i in range(0, len(segmentStart)):
            if segmentStart[i] > ((track["progress_ms"] / 1000) + delay + 1):
                segmentStartTimeLast = i
                break

        for i in range(segmentStartTimeFirst, segmentStartTimeLast):
            segmentStartIntervall["\"" + str(i-segmentStartTimeFirst) + "\""] = segmentStart[i]
            segmentDurationIntervall["\"" + str(i-segmentStartTimeFirst) + "\""] = segmentDuration[i]
            segmentConfidenceIntervall["\"" + str(i-segmentStartTimeFirst) + "\""] = segmentConfidence[i]
            segmentLoudnessSlopeIntervall["\"" + str(i-segmentStartTimeFirst) + "\""] = segmentLoudnessSlope[i]
            segmentLoudnessMaxIntervall["\"" + str(i-segmentStartTimeFirst) + "\""] = (segmentLoudnessMax[i] * -1) / 10

        beatStart = {}
        beatDuration = {}
        beatConfidence = {}

        actualBeatStartIndex = 0
        possibleBeatStartTime = 0
        possibleBeatStartIndex = 0

        actualBeatStart ={}
        actualBeatDuration ={}
        actualBeatConfidence ={}

        beatStartIntervall = {}
        beatDurationIntervall = {}
        beatConfidenceIntervall = {}

        i = 0
        for beats in analysis["beats"]:
                beatStart[i] = beats["start"]
                beatDuration[i] = beats["duration"]
                beatConfidence[i] = beats["confidence"]
                i = i + 1

        actualBeatListIndex = 0
        possibleBeatStartIndex = 0
        #print("beatStart: ", beatStart)
        logger.info("Count: %i", len(beatStart))
        for i in beatStart:
            if i == possibleBeatStartIndex:
                possibleBeatStartTime = beatStart[possibleBeatStartIndex]
                for j in range(i, len(beatStart) - i):
                    if(i+j == len(beatStart)):
                        break;
                    elif(beatStart[j+i] > possibleBeatStartTime + cooldown / 1000):
                        break;
                    elif(beatConfidence[j+i] > beatConfidence[possibleBeatStartIndex]):
                        possibleBeatStartTime = beatStart[i + j]
                        possibleBeatStartIndex = i + j
                actualBeatStartIndex = possibleBeatStartIndex
                possibleBeatStartIndex = possibleBeatStartIndex + 1

                actualBeatStart[actualBeatListIndex] = beatStart[actualBeatStartIndex]
                actualBeatDuration[actualBeatListIndex] = beatDuration[actualBeatStartIndex]
                actualBeatConfidence[actualBeatListIndex] = beatConfidence[actualBeatStartIndex]
                actualBeatListIndex = actualBeatListIndex + 1

        #print(actualBeatStart)

        beatStartTimeFirst = 0
        beatStartTimeLast = 0
        for i in range(0, len(actualBeatStart)):
            if actualBeatStart[i] > ((track["progress_ms"] - 3000) / 1000):
                beatStartTimeFirst = i
                break

        for i in range(0, len(actualBeatStart)):
            if actualBeatStart[i] > ((track["progress_ms"] / 1000) + delay + 1):
                beatStartTimeLast = i
                break

        for i in range(beatStartTimeFirst, beatStartTimeLast):
            beatStartIntervall["\"" + str(i-beatStartTimeFirst) + "\""] = actualBeatStart[i]
            beatDurationIntervall["\"" + str(i-beatStartTimeFirst) + "\""] =  actualBeatDuration[i]
            beatConfidenceIntervall["\"" + str(i-beatStartTimeFirst) + "\""] =  actualBeatConfidence[i]



        for i in beatStartIntervall:
            #print("slopeIntervall: ", loudnessSlopeIntervall[i])
            timeUntilStart = beatStartIntervall[i]-((track["progress_ms"]+offset)/1000)
            timeUntilStartHue = beatStartIntervall[i]-((track["progress_ms"]+offset+hueOffset)/1000)
            if timeUntilStart > 0:
                sc.enter(timeUntilStart, 1, evaluate, (sc,beatDurationIntervall[i], beatConfidenceIntervall[i]))
                sc.enter(timeUntilStartHue, 1, evaluateHue, (sc,beatDurationIntervall[i], beatConfidenceIntervall[i]))
        songID = trackId
    except spotipy.exceptions.SpotifyException:
        logger.error("Fehler mit den Berechtigungen")
    except TypeError:
        logger.error("Token abgelaufen oder Musik zu lange pausiert")

def clearHue():
    if bridgeEnabled:
        bridge.set_light(hueLamps, 'on', False)

def clearLight():
    if consoleEnabled:
        if platform.system() == "Windows":
            os.system('color 0f')
        if platform.system() == "Linux":
            os.system('setterm -background black -foreground white -store')
        if platform.system() == "Darwin":
            os.system('osascript -e \"tell application \\"Terminal\\" to set background color of window 1 to {0, 0, 0, 0}\"')

def remapValue(value):
    v = tan(sin(value*80))*0.35+0.5
    if v > 1:
        v = 1
    elif v < 0:
        v = 0
    return v

def valueToRGB(value):
    if value == 0:
        b = {}
        b["r"] = 0
        b["g"] = 0
        b["b"] = 0
        return b
    rgb = colorsys.hsv_to_rgb(remapValue(value),1, 1)
    a = {}
    a["r"] = rgb[0]*255
    a["g"] = rgb[1]*255
    a["b"] = rgb[2]*255
    return a

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
    a["v"] = brightness
    return a
def evaluateHue(sc, duration, value):
    if value > filter:
        rgb = valueToRGB(value)
        hsv = valueToHSV(value)
        if bridgeEnabled:
            bridge.set_light(hueLamps, 'on', True)
            bridge.set_light(hueLamps, 'hue', int(hsv["h"]))
            bridge.set_light(hueLamps, 'sat', int(hsv["s"]))
            bridge.set_light(hueLamps, 'bri', int(hsv["v"]))
            sc.enter(duration, 1, clearHue, ())
def evaluate(sc, duration, value):
    if value > filter:
        rgb = valueToRGB(value)
        hsv = valueToHSV(value)
        if mqttEnabled:
            mqttClient.publish("color", "{\"color\":" + str(rgb).replace("\'", "\"") + "}")
        if consoleEnabled:
            if platform.system() == "Windows":
                os.system('color 1f') # sets the background to blue
            if platform.system() == "Linux":
                os.system('setterm -background blue -foreground white -store')
            if platform.system() == "Darwin":
                rgb = valueToRGB(value)
                os.system('osascript -e \"tell application \\"Terminal\\" to set background color of window 1 to {' + str(int(rgb['r']/255*50000)) + ', ' + str(int(rgb['g']/255*50000)) + ', ' + str(int(rgb['b']/255*50000)) + ', 0}\"')
    sc.enter(duration, 1, clearLight, ())

def auth(username):
    token = util.prompt_for_user_token(username, scope="user-read-currently-playing")
    return token

if not debug:
    logging.basicConfig(level='INFO')
else:
    logging.basicConfig(level='DEBUG')
s = sched.scheduler(time.time, time.sleep)

os.environ["SPOTIPY_CLIENT_ID"] = "def1a61cd5434c3f8dd75740d2da049c"
os.environ["SPOTIPY_CLIENT_SECRET"] = "c847178ddadc4fd59b4f1e03508a05ba"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8080"
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
token = auth(username)
if mqttEnabled:
    mqttSetup()
if bridgeEnabled:
    bridge = Bridge(bridgeIp)
def loop(sc):
    if token:
        try:
            getCurrentTrack(token, sc)
        except spotipy.client.SpotifyException:
            getCurrentTrack(auth())
    else:
        logger.error("Bekomme keinen Token für Nutzer %s", username)
    s.enter(delay, 1, loop, (sc,))

try:
    s.enter(delay, 1, loop, (s,))
    s.run()
except KeyboardInterrupt:
    logger.info("Beende Programm!")
    clearLight()
    clearHue()
    if not s.empty():
        for event in s.queue:
            s.cancel(event)
            logger.debug("Beende %s", event)
