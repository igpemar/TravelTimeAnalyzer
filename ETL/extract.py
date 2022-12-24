import os
import sys
import time
import pandas
import random
import requests
import datetime
from filelock import FileLock
import config.config as config
import helpers.logger as logger


class TravelStats:
    def __init__(self):
        self.home2work = TravelTime()
        self.work2home = TravelTime()

    def loadH2WFromCSV(self, filename: str = "Output"):
        self.home2work.loadOutputFromCSV(filename)

    def loadW2FFromCSV(self, filename: str = "Output"):
        self.work2home.loadOutputFromCSV(filename)

    def getH2W(
        self,
    ):
        return self.home2work

    def getW2H(
        self,
    ):
        return self.work2home

    def flushStats(
        self,
    ):
        self.home2work.flushStats()
        self.work2home.flushStats()

    def incrementRequestIDs(self, inc: int):
        if not self.home2work.reqID:
            self.home2work.setReqID(1)
            self.work2home.setReqID(2)
        else:
            self.home2work.incrementReqID(inc)
            self.work2home.incrementReqID(inc)

    def decrementRequestIDs(self, inc: int):
        if not self.home2work.reqID:
            self.home2work.setReqID(1)
            self.work2home.setReqID(2)
        else:
            self.home2work.incrementReqID(-inc)
            self.work2home.incrementReqID(-inc)

    def setTimestamp(self, timestamp: datetime.datetime):
        self.home2work.setTimeStamps(timestamp)
        self.work2home.setTimeStamps(timestamp)


class TravelTime:
    def __init__(self):
        self.reqID = []
        self.timestampSTR = []
        self.timestampDT = []
        self.distanceAVG = []
        self.durationInclTraffic = []
        self.durationEnclTraffic = []
        self.isFirstWriteCycle = True

    def flushStats(
        self,
    ):
        self.restartReqID()
        self.timestampSTR = []
        self.timestampDT = []
        self.distanceAVG = []
        self.durationInclTraffic = []
        self.durationEnclTraffic = []
        self.isFirstWriteCycle = True

    def restartReqID(
        self,
    ):
        self.reqID = [self.reqID[-1]]

    def loadOutputFromCSV(self, filename: str):
        try:
            data = pandas.read_csv(filename, sep=";")
        except:
            logger.log(
                f"Error reading from {filename}, impossible to restart from existing data"
            )
            return

        for i in range(data.shape[0]):
            self.reqID.append(data.values[i][0])
            self.timestampSTR.append(data.values[i][1].strip())
            self.timestampDT.append(
                datetime.datetime.strptime(
                    data.values[i][1].strip(), "%Y-%m-%d %H:%M:%S"
                )
            )
            self.distanceAVG.append(data.values[i][2])
            self.durationInclTraffic.append(data.values[i][3])
            self.durationEnclTraffic.append(data.values[i][4])
            self.isFirstWriteCycle = False

    def setTimeStamps(self, timestamp: datetime.datetime):
        self.timestampDT.append(timestamp)
        self.timestampSTR.append(timestamp.strftime("%Y-%m-%d %H:%M:%S"))

    def setReqID(self, reqID: int):
        self.reqID = [reqID]

    def incrementReqID(self, incr: int):
        if self.isFirstWriteCycle:
            self.reqID[0] += incr
        else:
            self.reqID.append(self.reqID[-1] + incr)


class GoogleMapsRequests:
    def __init__(self):
        self.h2wRequest = ""
        self.workh2wRequest = ""

    def build_request(self, config: config.Config) -> tuple[str]:
        outputFormat = "json"
        requestStart = "https://maps.googleapis.com/maps/api/distancematrix/"
        startPoint = str(config.HOME[0]) + "%2C" + str(config.HOME[1])
        endPoint = str(config.WORK[0]) + "%2C" + str(config.WORK[1])
        self.h2wRequest = (
            requestStart
            + outputFormat
            + "?destinations="
            + endPoint
            + "&origins="
            + startPoint
            + "&mode=driving"
            + "&departure_time=now"
            + "&key="
            + config.API_KEY
        )
        self.w2hRequest = (
            requestStart
            + outputFormat
            + "?destinations="
            + startPoint
            + "&origins="
            + endPoint
            + "&mode=driving"
            + "&departure_time=now"
            + "&key="
            + config.API_KEY
        )


def restartCheck(FORCED_INPUT: str = "", sourcedata: str = "Output") -> TravelStats:
    while True:
        if FORCED_INPUT != "":
            s = FORCED_INPUT
        else:
            s = input(
                " Would you like to start from scratch and erase the existing data? Y/N/A "
            )
        res = TravelStats()
        if s == "A" or s == "A":
            sys.exit()
        elif s == "y" or s == "Y":
            clearOldExportFiles(sourcedata)
            res.home2work.reqID = [1]
            res.work2home.reqID = [2]
            return res
        elif s == "n" or s == "N":
            res.loadH2WFromCSV(sourcedata + "_h2w.csv")
            res.loadW2FFromCSV(sourcedata + "_w2h.csv")
            res.home2work.reqID = list(
                range(1, len(res.home2work.distanceAVG) * 2 + 2, 2)
            )
            res.work2home.reqID = list(
                range(2, len(res.home2work.distanceAVG) * 2 + 3, 2)
            )
            return res


def fetchData(sourcedata: str = "Output") -> TravelStats:
    res = TravelStats()
    res.loadH2WFromCSV(sourcedata + "_h2w.csv")
    res.loadW2FFromCSV(sourcedata + "_w2h.csv")
    res.home2work.reqID = list(range(1, len(res.home2work.distanceAVG) * 2 + 2, 2))
    res.work2home.reqID = list(range(2, len(res.home2work.distanceAVG) * 2 + 3, 2))
    return res


def sendRequest(config: config.Config, request: requests.request, reqID: int):
    payload, headers = {}, {}
    config.resetRetryCounter()
    while True:
        try:
            resp = requests.request("GET", request, headers=headers, data=payload)
            break
        except requests.ConnectionError:
            if config.RETRY_COUNTER < config.RETRY_MAX_TRIES:
                config.incRetryCounter()
                logger.log(
                    f"Request failed, retrying in {config.RETRY_INTERVAL} seconds; attempt {config.RETRY_COUNTER}/{config.RETRY_MAX_TRIES}"
                )
                time.sleep(config.RETRY_INTERVAL)
                continue
            else:
                logger.log(f"Max number of tries reached for Request {reqID}, exiting")
                sys.exit()

    config.resetRetryCounter()
    ok = handleResponse(resp)
    while not ok:
        if config.RETRY_COUNTER < config.RETRY_MAX_TRIES:
            config.incRetryCounter()
            logger.log(f"Response nopt OK, retrying in {config.RETRY_INTERVAL} seconds")
            time.sleep(config.RETRY_INTERVAL)
            continue
        else:
            logger.log(f"Max number of tries reached for Request {reqID}, exiting")
            sys.exit()

    return resp


def handleResponse(response: requests.Response) -> bool:
    if response.ok:
        elapsed = round(response.elapsed.microseconds / 1000, 1)
        logger.log("Request succeded, {elapsed} ms")
        return True
    else:
        logger.log("ERROR: An error occurred while performing the API requests")
        return False


def mockh2wResponseAsJson() -> str:
    duration_in_traffic = 900 + random.randint(-50, 50)
    duration = 800 + random.randint(-5, 5)
    distance = 5100 + random.randint(-1, 2) * 50
    return buildJson(duration_in_traffic, duration, distance)


def mockw2hResponseAsJson() -> str:
    duration_in_traffic = 950 + random.randint(-50, 50)
    duration = 850 + random.randint(-5, 5)
    distance = 5750 + random.randint(-1, 2) * 50
    return buildJson(duration_in_traffic, duration, distance)


def buildJson(duration_in_traffic: int, duration: int, distance: int):
    data = {}
    # elements["duration_in_traffic"] = str(duration_in_traffic)
    duration_in_traffic_value = {}
    duration_in_traffic_value = {"value": (duration_in_traffic)}
    duration_value = {"value": (duration)}
    distance_value = {"value": (distance)}
    elements_content = {
        "duration_in_traffic": duration_in_traffic_value,
        "duration": duration_value,
        "distance": distance_value,
    }
    elements = {"elements": [elements_content]}
    data["rows"] = [elements]
    return data


def clearOldExportFiles(sourcedata: str):
    if os.path.exists(sourcedata + "_h2w.csv"):
        os.remove(sourcedata + "_h2w.csv")
    if os.path.exists(sourcedata + "_w2h.csv"):
        os.remove(sourcedata + "_w2h.csv")
