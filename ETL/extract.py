import sys
import pandas
import datetime


class TravelStats:
    def __init__(self):
        self.home2work = TravelTime()
        self.work2home = TravelTime()

    def loadH2WFromCSV(self, filename):
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
        self.distanveAVG = []
        self.durationInclTraffic = []
        self.durationEnclTraffic = []

    def flushTravelTime(
        self,
    ):
        self.reqID = []
        c = []
        self.distanveAVG = []
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
            self.distanveAVG.append(data.values[i][2])
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


def restart_check():
    while True:
        s = input(
            " Would you like to start from scratch and erase the existing data? Y/N/A "
        )
        results = TravelStats()
        if s == "A" or s == "A":
            sys.exit()
        elif s == "y" or s == "Y":
            Restart_Flag = 1
            return (
                results,
                Restart_Flag,
            )
        elif s == "n" or s == "N":
            Restart_Flag = 0
            results.loadH2WFromCSV("Output_1.csv")
            results.loadW2FFromCSV("Output_2.csv")

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


def handleResponse(response) -> bool:
    if response.ok:
        print(f"{datetime.datetime.now()} ;  Request succeded")
        return True
    else:
        print(
            f"{datetime.datetime.now()} ;  ERROR: An error occurred while performing the API requests"
        )
        return False
