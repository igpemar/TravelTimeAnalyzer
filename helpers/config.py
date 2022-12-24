import os
import re
import sys
import configparser
import helpers.logger as logger
from datetime import datetime as datetime
from datetime import timedelta as timedelta


class Config:
    def __init__(self, REQ_SEND: bool):
        # Where to
        self.HOME = self.parseInputParam("HOME")
        self.WORK = self.parseInputParam("WORK")

        # Request Frequency
        self.HIGH_SAMPLING_FREQUENCY = self.parseInputParam("HIGH_SAMPLING_TIME")
        self.LOW_SAMPLING_FREQUENCY = self.parseInputParam("LOW_SAMPLING_TIME")
        self.DATA_DUMP_FREQUENCY = self.parseInputParam("DATA_DUMP_FREQUENCY")
        self.START_TIME = self.parseInputParam("START_TIME")
        self.initiateAPIkey()

        # Post processing
        self.POST_PROCESSING = self.parseInputParam("POST_PROCESSING")
        self.POST_PROCESSING_SAMPLING_TIME = self.parseInputParam(
            "POST_PROCESSING_SAMPLING_TIME"
        )

        # Request retry frequency
        self.RETRY_INTERVAL = 1  # seconds
        self.RETRY_COUNTER = 1
        self.RETRY_MAX_TRIES = 5
        self.REQ_SEND = REQ_SEND

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

    def parseInputParam(self, param: str):
        parser = configparser.ConfigParser()
        if os.path.exists("input.txt"):
            parser.read("input.txt")
            try:
                parsedParam = parser.get("Input Data", param)
            except configparser.NoOptionError:
                logger.log(
                    f"{param} not found in input.txt, unable to parse input data, exiting."
                )
            else:
                if parsedParam == "":
                    logger.log(f"Empty {param}, unable to parse input data, exiting.")
                else:
                    validParam = self.validateParam(param, parsedParam)
                    return validParam
        else:
            logger.log("input.txt not found, unable to parse input data, exiting.")
        sys.exit()

    def validateParam(self, paramName: str, paramValue: str):
        if paramName in ("WORK", "HOME"):
            pattern = re.compile("^\((-?\d{0,2}.\d*),\s?(-?\d{0,2}.\d*)\)$")
            a = re.findall(pattern, paramValue)
            if a:
                if len(a[0]) == 2:
                    return (float(a[0][0]), float(a[0][1]))
            logger.log(
                f"wrong input {paramName}, must be in (DD.DDDDDD, DD.DDDDDD) format, exiting."
            )
        elif paramName in (
            "HIGH_SAMPLING_TIME",
            "LOW_SAMPLING_TIME",
            "DATA_DUMP_FREQUENCY",
            "POST_PROCESSING_SAMPLING_TIME",
        ):
            if paramValue.isdigit():
                if int(paramValue) < 1:
                    logger.log(f"{paramName}, must be a >= 1")
                else:
                    return int(paramValue)
            else:
                logger.log(
                    f"wrong input {paramName}, must be a positive integer, exiting."
                )
        elif paramName == "START_TIME":
            try:
                return datetime.strptime(paramValue, "%Y-%m-%d %H:%M:%S")
            except:
                logger.log(
                    f"wrong input {paramName}, must be in a valid YYYY-MM-DD HH:MM:SS format, exiting."
                )
        elif paramName == "POST_PROCESSING":
            if paramValue.upper() in ("TRUE", "FALSE"):
                if paramValue.upper() == "TRUE":
                    return True
                elif paramValue.upper() == "FALSE":
                    return False
            else:
                logger.log(f"wrong input {paramName}, must be a boolean, exiting.")

        sys.exit()

    def incRetryCounter(
        self,
    ):
        self.RETRY_COUNTER += 1

    def resetRetryCounter(
        self,
    ):
        self.RETRY_COUNTER = 1
