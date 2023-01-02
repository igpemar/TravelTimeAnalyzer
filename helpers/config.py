import os
import re
import sys
import configparser
import helpers.logger as logger
from datetime import datetime as datetime
from datetime import timedelta as timedelta

REQ_SEND = 0
DATA_VALIDATION = True


class Config:
    def __init__(self):
        # Where to
        self.A = self.parseInput("Input Data", "FROM")
        self.B = self.parseInput("Input Data", "TO")

        # Request Frequency
        self.REQUEST_INTERVAL = self.parseInput("Input Data", "REQUEST_INTERVAL")
        self.REQUEST_INTERVAL_FINE = self.parseInput(
            "Optional", "REQUEST_INTERVAL_FINE"
        )
        if self.REQUEST_INTERVAL_FINE < self.REQUEST_INTERVAL:
            self.REQUEST_INTERVAL_FINE_TIMERANGES = self.parseInput(
                "Optional", "REQUEST_INTERVAL_FINE_TIMERANGES"
            )
        else:
            self.REQUEST_INTERVAL_FINE_TIMERANGES = []

        self.DATA_DUMP_INTERVAL = self.parseInput("Optional", "DATA_DUMP_INTERVAL")
        self.initiateAPIkey()

        # Post processing
        self.ENABLE_POST_PROCESSING = self.parseInput(
            "Input Data", "ENABLE_POST_PROCESSING"
        )
        self.POST_PROCESSING_INTERVAL = self.parseInput(
            "Optional", "POST_PROCESSING_INTERVAL"
        )

        # Delayed start
        self.START_TIME = self.parseInput("Optional", "START_TIME")

        # Programmed end
        self.END_TIME = self.parseInput("Optional", "END_TIME")

        # Request retry frequency
        self.RETRY_INTERVAL = 1  # seconds
        self.RETRY_COUNTER = 1
        self.RETRY_MAX_TRIES = 5
        self.REQ_SEND = REQ_SEND
        self.RETURNMODE = self.parseInput("Input Data", "ENABLE_RETURN_MODE")
        if self.B == "":
            self.RETURNMODE = False
            logger.log(f"Running in one-way only mode.")

        # Persist mode
        self.PERSIST_MODE = self.parseInput("Optional", "PERSIST_MODE")

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
                sys.exit(0)
            if parsedParam == "":
                if param in (
                    "START_TIME",
                    "END_TIME",
                    "DATA_DUMP_INTERVAL",
                    "POST_PROCESSING_INTERVAL",
                    "PERSIST_MODE",
                    "REQUEST_INTERVAL_FINE",
                    "REQUEST_INTERVAL_FINE_TIMERANGES",
                ):
                    # If the parameter is optional we return its default value
                    return self.defaultValue(param)
                else:
                    logger.log(f"Empty {param}, unable to parse input data, exiting.")
            else:
                validParam = self.validateParam(param, parsedParam)
                return validParam
        else:
            logger.log("input.txt not found, unable to parse input data, exiting.")
        sys.exit(0)

    def validateParam(self, paramName: str, paramValue: str):
        if paramName in ("TO", "FROM"):
            return self.validateCoordinates(paramName, paramValue)
        elif paramName in (
            "REQUEST_INTERVAL_FINE",
            "REQUEST_INTERVAL",
            "DATA_DUMP_INTERVAL",
            "POST_PROCESSING_INTERVAL",
        ):
            if DATA_VALIDATION:
                return self.validateIntervals(paramName, paramValue)
            else:
                return float(paramValue)
        elif paramName in ("START_TIME", "END_TIME"):
            return self.validateTimes(paramValue)
        elif paramName in ("ENABLE_POST_PROCESSING", "ENABLE_RETURN_MODE"):
            return self.validateBoolean(paramName, paramValue)
        elif paramName == "PERSIST_MODE":
            return self.validatePersist(paramName, paramValue)
        elif paramName == "REQUEST_INTERVAL_FINE_TIMERANGES":
            return self.validateTimeRanges(paramValue)
        sys.exit(0)

    def validateCoordinates(self, location: str, coordinates: str):
        pattern = re.compile("^\((-?\d{0,2}.\d*),\s?(-?\d{0,2}.\d*)\)$")
        matches = re.findall(pattern, coordinates)
        if matches:
            if len(matches[0]) == 2:
                return (float(matches[0][0]), float(matches[0][1]))
        logger.log(
            f"wrong input {location}, must be in (DD.DDDDDD, DD.DDDDDD) format, exiting."
        )
        sys.exit(0)

    def validateTimeRanges(self, timeranges):
        if self.checkForDecimalPoint(timeranges):
            logger.log(
                f"wrong input {timeranges}, cannot contain decimal point, exiting."
            )
            sys.exit(0)

        pattern = re.compile("\[?(-?\d{1,2}),?")
        matches = re.findall(pattern, timeranges)
        if matches:
            # Regex match is detected
            if len(matches) % 2 != 0:
                # Check for even number of interval limits
                logger.log(
                    f"wrong input {timeranges}, timeranges must contain an even number of parameters, exiting."
                )
            else:
                for i, match in enumerate(matches):
                    if self.checkForNegative(match):
                        # Positive integers only
                        logger.log(
                            f"wrong input {timeranges}, must contain only positive integers < 24, exiting."
                        )
                        sys.exit(0)
                    if int(match) > 23:
                        # Positive integers under 24 only
                        logger.log(
                            f"wrong input {timeranges}, must contain only positive integers < 24, exiting."
                        )
                        sys.exit(0)
                    if i == 0:
                        continue
                    if int(match) == 0:
                        # Edge case where one of the limit intervals is zero
                        if not self.checkForLastelement(i, matches):
                            logger.log(
                                f"wrong input {timeranges}, {match} can only be at the beginning and/or end of the timerange array, exiting."
                            )
                            sys.exit(0)
                        else:
                            break
                    elif int(match) <= int(matches[i - 1]):
                        # Check for strictly growing array
                        logger.log(
                            f"wrong input {timeranges}, must be in strictly growing order, exiting."
                        )
                        sys.exit(0)
                return [int(match) for match in matches]
        else:
            # Regex match is not detected
            if timeranges == "[]":
                logger.log("Empty timeranges, defaulting to constant interval mode.")
                return []
            logger.log(
                f"wrong input {timeranges}, must be in [HH, HH, ...] format, exiting."
            )
        sys.exit(0)

    def checkForDecimalPoint(self, string: str):
        pattern = re.compile("\.")
        if re.findall(pattern, string):
            return True
        return False

    def checkForNegative(self, string: str):
        return int(string) < 0

    def checkForLastelement(self, i: int, list: list):
        return i == len(list) - 1

    def validateTimes(self, time: str):
        try:
            return datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            logger.log(
                f"wrong input {time}, must be in valid YYYY-MM-DD HH:MM:SS format, exiting."
            )
            sys.exit(0)

    def validateBoolean(self, paramName: str, bool: str):
        if bool.upper() in ("TRUE", "FALSE"):
            if bool.upper() == "TRUE":
                return True
            elif bool.upper() == "FALSE":
                return False
        else:
            logger.log(f"wrong input {paramName}, must be boolean, exiting.")
            sys.exit(0)

    def validateIntervals(self, paramName: str, paramValue: str):
        if paramValue.isdigit():
            if int(paramValue) < 1:
                logger.log(f"{paramName}, must be >= 1")
            else:
                return int(paramValue)
        else:
            logger.log(f"wrong input {paramName}, must be a positive integer, exiting.")
        sys.exit(0)

    def validatePersist(self, paramName: str, paramValue: str):
        if paramValue in ("csv", "db"):
            return paramValue
        else:
            logger.log(f"wrong input {paramName}, must be either 'csv' or 'db'.")
            sys.exit(0)

    def defaultValue(self, param: str):
        if param == "START_TIME":
            logger.log(f"Empty {param}, defaulting to now.")
            return datetime.now()
        elif param == "END_TIME":
            return ""
        elif param == "DATA_DUMP_INTERVAL":
            return self.REQUEST_INTERVAL_FINE * 10
        elif param == "POST_PROCESSING_INTERVAL":
            return self.REQUEST_INTERVAL_FINE * 10
        elif param == "PERSIST_MODE":
            return "DB"
        elif param == "REQUEST_INTERVAL_FINE":
            return self.REQUEST_INTERVAL
        elif param == "REQUEST_INTERVAL_FINE_TIMERANGES":
            return []

    def incRetryCounter(
        self,
    ):
        self.RETRY_COUNTER += 1

    def resetRetryCounter(
        self,
    ):
        self.RETRY_COUNTER = 1
