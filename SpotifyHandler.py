import time
import spotipy
import logging
import sched
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime

class SpotifyHandler():
    logger = logging.getLogger('SpotifyLightIntegration')
    liModules = None
    username = ''
    songID = ''
    token = None
    #spotify eventuell nicht länger benötigt -> später testen
    #spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    sp = spotipy.Spotify(auth=token)
    sc = sched.scheduler(time.time, time.sleep)

    delay = 2
    progress = 0
    isPaused = False
    wasPaused = False
    progressTolerance = 5000
    features = None
    analysis = None
    startTime = None
    offset = 100
    cooldownBeats = 200
    filter = 0
    useBeats = True

    def __init__(self, username, liModules):
        self.username = username
        self.liModules = liModules

    def setup(self):
        self.token = util.prompt_for_user_token(self.username, scope="user-read-currently-playing")
    def loop(self):
        if self.token:
            try:
                self.getCurrentTrack()
            except spotipy.client.SpotifyException:
                self.logger.error("Fehler mit den Berechtigungen! Bitte Token-Scope prüfen.")
                auth()
        else:
            self.logger.error("Bekomme keinen Token für Nutzer %s.", username)
        self.sc.enter(self.delay, 1, self.loop, ())
        self.sc.run()

    def sendOnCommandBeats(self, duration, confidence, start):
        if confidence > self.filter:
            for m in self.liModules:
                m.sendColor(confidence)
                self.sc.enter(duration, 1, m.clearColor, ())

    def getCurrentTrack(self):
        sp = spotipy.Spotify(auth=self.token)
        track = sp.current_user_playing_track()
        if track["is_playing"] is not True:
            if self.wasPaused is not True:
                for i in self.sc.queue:
                    self.sc.cancel(i)
                self.wasPaused = True
            #FIXME: Licht hier eventuell per clearLight() ausschalten!
            self.logger.info("Wiedergabe pausiert!")
        else:
            self.logger.debug(str(track["item"]["name"]))
            self.logger.debug(track["progress_ms"] - self.delay*1000 - self.progress)
            trackId = str(track["item"]["id"])
            if(track["progress_ms"] - self.delay*1000 >= self.progress + self.progressTolerance or track["progress_ms"] - self.delay*1000 <= self.progress - self.progressTolerance or trackId != self.songID or self.wasPaused is True):
                if self.wasPaused is True:
                    self.logger.info("Wiedergabe läuft!")
                    self.wasPaused = False
                for i in self.sc.queue:
                    self.sc.cancel(i)
                if trackId != self.songID:
                    self.logger.info("Neues Lied: " + str(track["item"]["name"]) + " mit der ID: " + str(trackId))
                elif track["progress_ms"] - self.delay*1000 >= self.progress + self.progressTolerance or track["progress_ms"] - self.delay*1000 <= self.progress - self.progressTolerance:
                    self.logger.info("Es wurde vor- oder zurück-gespult, passe Lichter an!")
                self.features = sp.audio_features(trackId)
                self.analysis = sp.audio_analysis(trackId)
                self.startTime = datetime.now()
### Tempo Analyse Marker
                #if useTempo:
                #    tempoStart = {}
                #    tempo = features[0]["tempo"]
                #    i = 0
                #    tempoStart[i] = 0;
                #    while(tempoStart[i] <= track["item"]["duration_ms"] / 1000):
                #        tempoStart[i+1] = (i+1) * 60/tempo
                #        i = i + 1
                #    tempoStartTimeFirst = 0
                #    for i in range(0, len(tempoStart)):
                #        if tempoStart[i] > ((track["progress_ms"]) / 1000):
                #            tempoStartTimeFirst = i
                #            break
                #    for i in range(tempoStartTimeFirst, len(tempoStart)):
                #        timeUntilStart = tempoStart[i]-((track["progress_ms"]+offset)/1000)
                #        if timeUntilStart > 0:
                #            #FIXME sendOnCommandTempo erstellen
                #            sc.enter(timeUntilStart - 0.05, 1, sendOnCommandTempo, (sc, 0, 0))
                i = 0;
                sectionStart = {}
                sectionKey = {}
                sectionMode = {}
                for segment in self.analysis["sections"]:
                    sectionStart[i] = segment["start"]
                    sectionKey[i] = segment["key"]
                    sectionMode[i] = segment["mode"]
                    i = i + 1

                sectionStartTimeFirst = 0
                for i in range(0, len(sectionStart)):
                    if sectionStart[i] > ((track["progress_ms"]) / 1000):
                        sectionStartTimeFirst = i
                        break
                #FIXME: printSection bauen
                #for i in range(sectionStartTimeFirst, len(sectionStart)):
                #    timeUntilStart = sectionStart[i]-((track["progress_ms"]+self.offset)/1000)
                #    if timeUntilStart > 0:
                #        self.sc.enter(timeUntilStart, 1, printSection, (sc, sectionKey[i], sectionMode[i]))
### Segment Analyse Marker
                #if useSegments:
                #    segmentStart = {}
                #    segmentDuration = {}
                #    segmentConfidence = {}
                #    segmentLoudnessStart = {}
                #    segmentLoudnessMax = {}
                #    segmentLoudnessMaxTime = {}
                #    segmentLoudnessDifferenceStartMax = {}
                #    segmentLoudnessSlope = {}
                #    segmentLoudnessValue = {}
                #
                #    actualSegmentStart = {}
                #    actualSegmentDuration = {}
                #    actualSegmentLoudnessValue = {}
                #
                #    segmentStartIntervall = {}
                #    segmentDurationIntervall = {}
                #    segmentLoudnesValueIntervall = {}
                #
                #    i = 0;
                #
                #    for segment in analysis["segments"]:
                #        segmentStart[i] = segment["start"]
                #        segmentDuration[i] = segment["duration"]
                #        segmentConfidence[i] = segment["confidence"]
                #        segmentLoudnessStart[i] = segment["loudness_start"]
                #        segmentLoudnessMax[i] = ((segment["loudness_max"])* 1)
                #        segmentLoudnessMaxTime[i] = ((segment["loudness_max_time"]) * 1000) + 1
                #        segmentLoudnessDifferenceStartMax[i] = abs(segmentLoudnessStart[i]) - abs(segmentLoudnessMax[i])
                #        segmentLoudnessSlope[i] = (segmentLoudnessDifferenceStartMax[i] / segmentLoudnessMaxTime[i]) * 2
                #        segmentLoudnessValue[i] = 0.8 * segmentLoudnessMax[i] + 0.2 * segmentLoudnessSlope[i]
                #        i = i + 1
                #
                #    possibleSegmentStartTime = 0
                #    possibleSegmentStartIndex = 0
                #    actualSegmentStartIndex = 0
                #    actualSegmentListIndex = 0
                #
                #    for i in segmentStart:
                #        if i == possibleSegmentStartIndex:
                #            possibleSegmentStartTime = segmentStart[possibleSegmentStartIndex]
                #            for j in range(i, len(segmentStart) - i):
                #                if(i+j == len(segmentStart)):
                #                    break;
                #                elif(segmentStart[j+i] > possibleSegmentStartTime + cooldownSegments / 1000):
                #                    break;
                #                elif(segmentLoudnessValue[j+i] > segmentLoudnessValue[possibleSegmentStartIndex]):
                #                    possibleSegmentStartTime = segmentStart[i + j]
                #                    possibleSegmentStartIndex = i + j
                #            actualSegmentStartIndex = possibleSegmentStartIndex
                #            possibleSegmentStartIndex = possibleSegmentStartIndex + 5
                #            actualSegmentStart[actualSegmentListIndex] = segmentStart[actualSegmentStartIndex]
                #            actualSegmentDuration[actualSegmentListIndex] = segmentDuration[actualSegmentStartIndex]
                #            actualSegmentLoudnessValue[actualSegmentListIndex] = segmentLoudnessValue[actualSegmentStartIndex]
                #            actualSegmentListIndex = actualSegmentListIndex + 1
                #
                #    segmentStartTimeFirst = 0
                #    for i in range(0, len(actualSegmentStart)):
                #        if actualSegmentStart[i] > ((track["progress_ms"]) / 1000):
                #            segmentStartTimeFirst = i
                #            break
                #
                #    for i in range(segmentStartTimeFirst, len(actualSegmentStart)):
                #        timeUntilStart = actualSegmentStart[i]-((track["progress_ms"]+offset)/1000)
                #        if timeUntilStart > 0:
                #            sc.enter(timeUntilStart, 1, sendOnCommandSegments, (sc,actualSegmentDuration[i], actualSegmentLoudnessValue[i]))
### Beats Analyse Marker
                if self.useBeats:
                    beatStartUnfiltered = {}
                    beatDurationUnfiltered = {}
                    beatConfidenceUnfiltered = {}

                    beatStart = {}
                    beatDuration = {}
                    beatConfidence = {}

                    actualBeatStartIndex = 0
                    possibleBeatStartTime = 0
                    possibleBeatStartIndex = 0

                    actualBeatStart = {}
                    actualBeatDuration = {}
                    actualBeatConfidence = {}

                    beatStartIntervall = {}
                    beatDurationIntervall = {}
                    beatConfidenceIntervall = {}

                    beatConfidenceFilter = 0.1

                    filterOverrideConfidence = 0.5

                    i = 0
                    for beats in self.analysis["beats"]:
                            beatStartUnfiltered[i] = beats["start"]
                            beatDurationUnfiltered[i] = beats["duration"]
                            beatConfidenceUnfiltered[i] = beats["confidence"]
                            i = i + 1
                    j = 0
                    for i in beatConfidenceUnfiltered:
                        if(beatConfidenceUnfiltered[i] >= beatConfidenceFilter):
                            beatStart[j] = beatStartUnfiltered[i]
                            beatDuration[j] = beatDurationUnfiltered[i]
                            beatConfidence[j] = beatConfidenceUnfiltered[i]
                            j = j + 1

                    actualBeatListIndex = 0
                    possibleBeatStartIndex = 0
                    for i in beatStart:
                        if i == possibleBeatStartIndex:
                            possibleBeatStartTime = beatStart[possibleBeatStartIndex]
                            for j in range(i, len(beatStart) - i):
                                if(beatConfidence[j+i] >= filterOverrideConfidence):
                                    actualBeatStartIndex = possibleBeatStartIndex
                                    possibleBeatStartIndex = possibleBeatStartIndex + 1

                                    actualBeatStart[actualBeatListIndex] = beatStart[actualBeatStartIndex]
                                    actualBeatDuration[actualBeatListIndex] = beatDuration[actualBeatStartIndex]
                                    actualBeatConfidence[actualBeatListIndex] = beatConfidence[actualBeatStartIndex]
                                    actualBeatListIndex = actualBeatListIndex + 1
                                    break;
                                elif(i+j == len(beatStart)):
                                    break;
                                elif(beatStart[j+i] > possibleBeatStartTime + self.cooldownBeats / 1000):
                                    break;
                                elif(beatConfidence[j+i] > beatConfidence[possibleBeatStartIndex]):
                                    possibleBeatStartTime = beatStart[i + j]
                                    possibleBeatStartIndex = i + j
                            actualBeatStartIndex = possibleBeatStartIndex
                            #possibleBeatStartIndex = possibleBeatStartIndex + 1

                            for k in beatStart:
                                if(beatStart[k] >= beatStart[actualBeatStartIndex] + self.cooldownBeats / 1000):
                                    possibleBeatStartIndex = k
                                    break;

                            actualBeatStart[actualBeatListIndex] = beatStart[actualBeatStartIndex]
                            actualBeatDuration[actualBeatListIndex] = beatDuration[actualBeatStartIndex]
                            actualBeatConfidence[actualBeatListIndex] = beatConfidence[actualBeatStartIndex]
                            actualBeatListIndex = actualBeatListIndex + 1


                    beatStartTimeFirst = 0
                    for i in range(0, len(actualBeatStart)):
                        if actualBeatStart[i] > ((track["progress_ms"] - 3000) / 1000):
                            beatStartTimeFirst = i
                            break

                    for i in range(beatStartTimeFirst, len(actualBeatStart)):
                        currentTime = datetime.now()
                        timeDifference = currentTime - self.startTime
                        timeDifferenceMilliseconds = timeDifference.seconds * 1000 + timeDifference.microseconds / 1000
                        timeUntilStart = actualBeatStart[i]-((track["progress_ms"]+self.offset+timeDifferenceMilliseconds)/1000)
                        if timeUntilStart > 0:
                            self.sc.enter(timeUntilStart, 1, self.sendOnCommandBeats, (actualBeatDuration[i], actualBeatConfidence[i], actualBeatStart[i]))
#Finales Zeug
            self.songID = trackId
            self.progress = track["progress_ms"]
