import csv
import helpers.logger as logger
import helpers.config as config
from datetime import datetime as datetime
import db.connector as db


class TravelStats:
    def __init__(self):
        self.home2work = TravelTime()
        self.work2home = TravelTime()
        self.initiateRequestIDs()

    def loadH2WFromCSV(self, filename: str = "Output"):
        self.home2work.loadOutputFromCSV(filename)

    def loadW2FFromCSV(self, filename: str = "Output"):
        self.work2home.loadOutputFromCSV(filename)

    def loadH2WFromDB(self):
        self.home2work.loadOutputFromDB("H2W")

    def loadW2HFromDB(self):
        self.work2home.loadOutputFromDB("W2H")

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

    def initiateRequestIDs(self):
        self.home2work.reqID = [1]
        self.work2home.reqID = [2]

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

    def setTimestamp(self, timestamp: datetime):
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
            with open(filename, "r") as f:
                csvreader = csv.reader(f, delimiter=";")
                next(csvreader)
                data = []
                for row in csvreader:
                    data.append(row)
        except FileNotFoundError:
            return
        except StopIteration:
            return
        except:
            logger.log(
                f"Error reading from {filename}, impossible to restart from existing data"
            )
            return
        self.parseData(data)

    def parseData(self, data: list):
        for _, value in enumerate(data):
            self.reqID.append(float(value[0]))
            self.timestampSTR.append(value[1].strip())
            self.timestampDT.append(
                datetime.strptime(value[1].strip(), "%Y-%m-%d %H:%M:%S")
            )
            self.distanceAVG.append(float(value[2]))
            self.durationInclTraffic.append(float(value[3]))
            self.durationEnclTraffic.append(float(value[4]))
            self.isFirstWriteCycle = False

    def loadOutputFromDB(self, tableName: str):
        dbConfig = db.getDBConfig()
        conn = db.connect2DB(dbConfig)
        data = db.getAll(conn, tableName)
        db.closedbconnection(conn)
        self.parseData(data)

    def setTimeStamps(self, timestamp: datetime):
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
        baseURL = "https://maps.googleapis.com/maps/api/distancematrix/"
        startPoint = str(config.HOME[0]) + "%2C" + str(config.HOME[1])
        endPoint = str(config.WORK[0]) + "%2C" + str(config.WORK[1])
        self.h2wRequest = (
            baseURL
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
            baseURL
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
