import csv
import helpers.logger as logger
import helpers.config as config
from datetime import datetime as datetime
import db.connector as db


class TravelStats:
    def __init__(self):
        self.A2B = TravelTime()
        self.B2A = TravelTime()
        self.initiateRequestIDs()

    def loadA2BFromCSV(self, filename: str = "Output"):
        self.A2B.loadOutputFromCSV(filename)

    def loadB2AFromCSV(self, filename: str = "Output"):
        self.B2A.loadOutputFromCSV(filename)

    def loadA2BFromDB(self):
        self.A2B.loadOutputFromDB("A2B")

    def loadB2AFromDB(self):
        self.B2A.loadOutputFromDB("B2A")

    def getA2B(
        self,
    ):
        return self.A2B

    def getB2A(
        self,
    ):
        return self.B2A

    def flushA2BStats(
        self,
    ):
        self.A2B.flushStats()

    def flushB2AStats(
        self,
    ):
        self.B2A.flushStats()

    def initiateRequestIDs(self):
        self.A2B.reqID = [1]
        self.B2A.reqID = [2]

    def incrementRequestIDs(self, inc: int):
        if not self.A2B.reqID:
            self.A2B.setReqID(1)
            self.B2A.setReqID(2)
        else:
            self.A2B.incrementReqID(inc)
            self.B2A.incrementReqID(inc)

    def decrementRequestIDs(self, inc: int):
        if not self.A2B.reqID:
            self.A2B.setReqID(1)
            self.B2A.setReqID(2)
        else:
            self.A2B.incrementReqID(-inc)
            self.B2A.incrementReqID(-inc)

    def setTimestamp(self, timestamp: datetime):
        self.A2B.setTimeStamps(timestamp)
        self.B2A.setTimeStamps(timestamp)


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
            self.reqID.append(int(value[0]))
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
        db.closeDBconnection(conn)
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
        self.A2BRequest = ""
        self.B2ARequest = ""

    def build_request(self, config: config.Config) -> tuple[str]:
        outputFormat = "json"
        baseURL = "https://maps.googleapis.com/maps/api/distancematrix/"
        startPoint = str(config.A[0]) + "%2C" + str(config.A[1])
        endPoint = str(config.B[0]) + "%2C" + str(config.B[1])
        self.A2BRequest = (
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
        self.B2ARequest = (
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
