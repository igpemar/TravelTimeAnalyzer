import os
import re
import sys
import configparser
import helpers.logger as logger
from datetime import datetime as datetime
from datetime import timedelta as timedelta

REQ_SEND = 0
DATA_VALIDATION = False
PERSIST_MODE = "db"  # choose between CSV and DB


class Config:
    def __init__(self):
        # Where to
        self.A = self.parseInput("Input Data", "FROM")
        self.B = self.parseInput("Input Data", "TO")

        # Request Frequency
        self.HIGH_SAMPLING_FREQUENCY = self.parseInput(
            "Input Data", "REQUEST_INTERVAL_HIGH"
        )
        self.LOW_SAMPLING_FREQUENCY = self.parseInput(
            "Input Data", "REQUEST_INTERVAL_LOW"
        )
        self.DATA_DUMP_INTERVAL = self.parseInput("Input Data", "DATA_DUMP_INTERVAL")
        self.initiateAPIkey()

        # Post processing
        self.POST_PROCESSING = self.parseInput("Input Data", "POST_PROCESSING")
        self.POST_PROCESSING_INTERVAL = self.parseInput(
            "Input Data", "POST_PROCESSING_INTERVAL"
        )

        # Delayed start
        self.START_TIME = self.parseInput("Optional", "START_TIME")

        # Request retry frequency
        self.RETRY_INTERVAL = 1  # seconds
        self.RETRY_COUNTER = 1
        self.RETRY_MAX_TRIES = 5
        self.REQ_SEND = REQ_SEND

        # Persist mode
        self.PERSIST_MODE = PERSIST_MODE

    def initiateAPIkey(
        self,
    ):
        self.API_KEY = ""
        secret = configparser.ConfigParser()
        if os.path.exists("secrets/google.txt"):
            secret.read("secrets/google.txt")
            try:
                self.API_KEY = secret.get("secrets", "API_KEY")
            except configparser.NoOptionError:
                self.REQ_SEND = 0
                logger.log(
                    "API_KEY not found in secrets/google.txt, defaulting to mock request mode."
                )
                logger.log("Press any key to continue...")
                input("")
            else:
                if self.API_KEY == "":
                    self.REQ_SEND = 0
                    logger.log("Empty API_KEY, defaulting to mock request mode.")
                    logger.log("Press any key to continue...")
                    input("")
        else:
            self.REQ_SEND = 0
            logger.log("secrets/google.txt not found, defaulting to mock request mode.")
            logger.log("Press any key to continue...")
            input("")
            return

    def getApiKey(
        self,
    ):
        return self.API_KEY

    def parseInput(self, section: str, param: str):
        parser = configparser.ConfigParser()
        if os.path.exists("input.txt"):
            parser.read("input.txt")
            try:
                parsedParam = parser.get(section, param)
            except configparser.NoOptionError:
                logger.log(
                    f"{param} not found in input.txt, unable to parse input data, exiting."
                )
            else:
                if parsedParam == "":
                    if param == "START_TIME":
                        return self.defaultValue(param)
                    else:
                        logger.log(
                            f"Empty {param}, unable to parse input data, exiting."
                        )
                else:
                    validParam = self.validateParam(param, parsedParam)
                    return validParam
        else:
            logger.log("input.txt not found, unable to parse input data, exiting.")
        sys.exit(1)

    def validateParam(self, paramName: str, paramValue: str):
        if paramName in ("TO", "FROM"):
            return self.validateCoordinates(paramName, paramValue)
        elif paramName in (
            "REQUEST_INTERVAL_HIGH",
            "REQUEST_INTERVAL_LOW",
            "DATA_DUMP_INTERVAL",
            "POST_PROCESSING_INTERVAL",
        ):
            if DATA_VALIDATION:
                return self.validateIntervals(paramName, paramValue)
            else:
                return float(paramValue)
        elif paramName == "START_TIME":
            return self.validateStartTime(self, paramName)
        elif paramName == "POST_PROCESSING":
            return self.validateBoolean(paramName, paramValue)
        sys.exit(1)

    def validateCoordinates(self, location: str, coordinates: str):
        pattern = re.compile("^\((-?\d{0,2}.\d*),\s?(-?\d{0,2}.\d*)\)$")
        matches = re.findall(pattern, coordinates)
        if matches:
            if len(matches[0]) == 2:
                return (float(matches[0][0]), float(matches[0][1]))
        logger.log(
            f"wrong input {location}, must be in (DD.DDDDDD, DD.DDDDDD) format, exiting."
        )
        sys.exit(1)

    def validateStartTime(self, start_time: str):
        try:
            return datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            logger.log(
                f"wrong input {start_time}, must be in valid YYYY-MM-DD HH:MM:SS format, exiting."
            )
            sys.exit(1)

    def validateBoolean(self, paramName: str, bool: str):
        if bool.upper() in ("TRUE", "FALSE"):
            if bool.upper() == "TRUE":
                return True
            elif bool.upper() == "FALSE":
                return False
        else:
            logger.log(f"wrong input {paramName}, must be boolean, exiting.")
            sys.exit(1)

    def validateIntervals(self, paramName: str, paramValue: str):
        if paramValue.isdigit():
            if int(paramValue) < 1:
                logger.log(f"{paramName}, must be >= 1")
            else:
                return int(paramValue)
        else:
            logger.log(f"wrong input {paramName}, must be a positive integer, exiting.")
            sys.exit(1)

    def defaultValue(self, param: str):
        if param == "START_TIME":
            logger.log(f"Empty {param}, defaulting to now.")
            return datetime.now()

    def incRetryCounter(
        self,
    ):
        self.RETRY_COUNTER += 1

    def resetRetryCounter(
        self,
    ):
        self.RETRY_COUNTER = 1
