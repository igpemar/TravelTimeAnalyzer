import sys
import json
import time
import pandas
import requests
import datetime


class TravelStats:
    def __init__(self):
        self.home2work = TravelTime()
        self.work2home = TravelTime()

    def loadH2WFromCSV(self, filename="Output"):
        self.home2work.loadOutputFromCSV(filename)

    def loadW2FFromCSV(self, filename):
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
        self.home2work.flushTravelTime()
        self.work2home.flushTravelTime()

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

    def setTimestamp(self, timestamp):
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

    def flushTravelTime(
        self,
    ):
        self.reqID = []
        c = []
        self.distanceAVG = []
        self.durationInclTraffic = []
        self.durationEnclTraffic = []

    def loadOutputFromCSV(self, filename: str):
        try:
            data = pandas.read_csv(filename, sep=";")
        except:
            print(
                f"Error reading from {filename} were found, impossible to restart from existing data, exiting ..."
            )
            sys.exit()

        print(f"Succesfully loaded {data.shape[0]} rows from {filename}")
        for i in range(data.shape[0]):
            self.reqID.append(data.values[i][0])
            self.timestampSTR.append(data.values[i][1].strip())
            self.distanceAVG.append(data.values[i][2])
            self.durationInclTraffic.append(data.values[i][3])
            self.durationEnclTraffic.append(data.values[i][4])

    def setTimeStamps(self, timestamp):
        self.timestampSTR.append(
            str(timestamp.year)
            + "-"
            + f"{timestamp.month:02}"
            + "-"
            + f"{timestamp.day:02}"
            + " "
            + f"{timestamp.hour:02}"
            + ":"
            + f"{timestamp.minute:02}"
            + ":"
            + f"{timestamp.second:02}"
        )
        self.timestampDT.append(timestamp)

    def setReqID(self, reqID: int):
        self.reqID = [reqID]

    def incrementReqID(self, incr: int):
        self.reqID.append(self.reqID[-1] + incr)


def restart_check(FORCED_INPUT="", sourcedata="Output"):
    while True:
        if FORCED_INPUT != "":
            s = FORCED_INPUT
        else:
            s = input(
                " Would you like to start from scratch and erase the existing data? Y/N/A "
            )
        results = TravelStats()
        if s == "A" or s == "A":
            sys.exit()
        elif s == "y" or s == "Y":
            Restart_Flag = 1
            results.home2work.reqID = [1]
            results.work2home.reqID = [2]
            return (
                results,
                Restart_Flag,
            )
        elif s == "n" or s == "N":
            Restart_Flag = 0
            results.loadH2WFromCSV(sourcedata + "_h2w.csv")
            results.loadW2FFromCSV(sourcedata + "_w2h.csv")
            results.home2work.reqID = list(
                range(1, len(results.home2work.distanceAVG) * 2 + 2, 2)
            )
            results.work2home.reqID = list(
                range(2, len(results.home2work.distanceAVG) * 2 + 3, 2)
            )

            return (
                results,
                Restart_Flag,
            )


def build_request(config) -> tuple[str]:
    outputFormat = "json"
    requestStart = "https://maps.googleapis.com/maps/api/distancematrix/"
    startPoint = str(config.HOME[0]) + "%2C" + str(config.HOME[1])
    endPoint = str(config.WORK[0]) + "%2C" + str(config.WORK[1])
    h2wRequest = (
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
    w2hRequest = (
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

    return h2wRequest, w2hRequest


def sendRequest(config, request, reqID):
    payload, headers = {}, {}
    config.resetRetryCounter()
    while True:
        try:
            resp = requests.request("GET", request, headers=headers, data=payload)
            break
        except requests.ConnectionError:
            if config.RETRY_COUNTER < config.RETRY_MAX_TRIES:
                config.incRetryCounter()
                print(
                    f"Request failed, retrying in {config.RETRY_INTERVAL} seconds; attempt {config.RETRY_COUNTER}/{config.RETRY_MAX_TRIES}"
                )
                time.sleep(config.RETRY_INTERVAL)
                continue
            else:
                print(f"Max number of tries reached for Request {reqID}, exiting")
                sys.exit()

    config.resetRetryCounter()
    ok = handleResponse(resp)
    while not ok:
        if config.RETRY_COUNTER < config.RETRY_MAX_TRIES:
            config.incRetryCounter()
            print(f"Response nopt OK, retrying in {config.RETRY_INTERVAL} seconds")
            time.sleep(config.RETRY_INTERVAL)
            continue
        else:
            f"Max number of tries reached for Request {reqID}, exiting"
            sys.exit()

    return resp


def handleResponse(response) -> bool:
    if response.ok:
        print(f"{datetime.datetime.now()} ;  Request succeded")
        return True
    else:
        print(
            f"{datetime.datetime.now()} ;  ERROR: An error occurred while performing the API requests"
        )
        return False


def mockh2wResponseAsJson() -> str:
    return json.loads(
        '{"rows":[{"elements":[{"duration_in_traffic": {"value": 900},"duration": {"value": 800},"distance": {"value": 5100}}]}]}'
    )


def mockw2hResponseAsJson() -> str:
    return json.loads(
        '{"rows":[{"elements":[{"duration_in_traffic": {"value": 950},"duration": {"value": 850},"distance": {"value": 5750}}]}]}'
    )
