import configparser
import datetime


HOME = (55.688519, 12.528168)  # GPS Coordinates in decimal degrees DDD.DDDDD
WORK = (55.672162, 12.585666)  # GPS Coordinates in decimal degrees DDD.DDDDD

DATA_DUMP_FREQUENCY = 10  # In seconds (integer)

HIGH_SAMPLING_FREQUENCY = 1  # In seconds Integer
LOW_SAMPLING_FREQUENCY = 1200  # In Seconds Integer

START_TIME = datetime.datetime(2022, 12, 11, 20, 26, 0)

Req_send = 1


class Config:
    def __init__(self):
        self.HOME = HOME
        self.WORK = WORK
        self.DATA_DUMP_FREQUENCY = DATA_DUMP_FREQUENCY
        self.HIGH_SAMPLING_FREQUENCY = HIGH_SAMPLING_FREQUENCY
        self.LOW_SAMPLING_FREQUENCY = LOW_SAMPLING_FREQUENCY
        self.START_TIME = START_TIME
        self.API_KEY = ""

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
