import time
import datetime
import configparser


HOME = (55.688519, 12.528168)  # GPS Coordinates in decimal degrees DDD.DDDDD
WORK = (55.672162, 12.585666)  # GPS Coordinates in decimal degrees DDD.DDDDD

DATA_DUMP_FREQUENCY = 1  # In seconds (integer)

HIGH_SAMPLING_TIME = 1  # In seconds Integer
LOW_SAMPLING_TIME = 1200  # In Seconds Integer

START_TIME = datetime.datetime(2022, 12, 12, 18, 9, 0)

Req_send = 1


class Config:
    def __init__(self, REQ_SEND):
        self.HOME = HOME
        self.WORK = WORK
        self.DATA_DUMP_FREQUENCY = DATA_DUMP_FREQUENCY
        self.HIGH_SAMPLING_FREQUENCY = HIGH_SAMPLING_TIME
        self.LOW_SAMPLING_FREQUENCY = LOW_SAMPLING_TIME
        self.START_TIME = START_TIME
        self.initiateAPIkey()

        self.RETRY_INTERVAL = 1  # seconds
        self.RETRY_COUNTER = 1
        self.RETRY_MAX_TRIES = 5
        self.REQ_SEND = REQ_SEND

    def initiateAPIkey(
        self,
    ):
        secret = configparser.ConfigParser()
        secret.read("secrets/google.txt")
        self.API_KEY = secret.get("secrets", "API_KEY")

    def getApiKey(
        self,
    ):
        return self.API_KEY

    def incRetryCounter(
        self,
    ):
        self.RETRY_COUNTER += 1

    def resetRetryCounter(
        self,
    ):
        self.RETRY_COUNTER = 1


def isItTimeToStart(start_time) -> bool:
    return start_time - datetime.datetime.now() > datetime.timedelta(seconds=1)


def isItTimeToDumpData(timeSinceLastDataDump, config) -> bool:
    return timeSinceLastDataDump >= datetime.timedelta(
        seconds=config.DATA_DUMP_FREQUENCY, microseconds=10
    )


def findwaittime(time, hdsf, ldsf):
    if time.weekday():
        h = time.hour
        if 5 <= h < 11 or 13 <= h < 19:
            return hdsf
    return ldsf


def waitForNextCycle(reqTimestamp, config):
    wait_time = findwaittime(
        reqTimestamp, config.HIGH_SAMPLING_FREQUENCY, config.LOW_SAMPLING_FREQUENCY
    )
    print(
        str(reqTimestamp)[0:-7]
        + " ; - Waiting "
        + str(wait_time)
        + " second(s) for next request cycle-"
    )
    print(str(reqTimestamp)[0:-7] + " ; ----------------------------------------------")
    time.sleep(wait_time)
