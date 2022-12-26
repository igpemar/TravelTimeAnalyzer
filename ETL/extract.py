import os
import sys
import time
import random
import requests
import db.connector as db
import helpers.config as config
import helpers.logger as logger
import helpers.datastructures as ds
from datetime import datetime as datetime


def restartCheck(
    FORCED_INPUT: str = "", persist: str = "CSV", sourcedata: str = "Output"
) -> ds.TravelStats:
    while True:
        if FORCED_INPUT != "":
            s = FORCED_INPUT
        else:
            s = input(
                " Would you like to start from scratch and erase the existing data? Y/N/A "
            )
        res = ds.TravelStats()
        if s == "A" or s == "A":
            logger.log("Abort")
            sys.exit(0)
        elif s == "y" or s == "Y":
            if persist.upper() == "CSV":
                clearOldExportFiles(sourcedata)
            elif persist.upper() == "DB":
                db.flushdbs(db.connect2DB(db.getDBConfig()))
            res.initiateRequestIDs()
            return res
        elif s == "n" or s == "N":
            if persist.upper() == "CSV":
                res.loadH2WFromCSV(sourcedata + "_h2w.csv")
                res.loadW2FFromCSV(sourcedata + "_w2h.csv")
            elif persist.upper() == "DB":
                res.loadH2WFromDB()
                res.loadW2HFromDB()
            else:
                logger.log(f"Wrong persist mode: {persist}, must be 'csv' or 'db'")

            res.home2work.reqID = list(
                range(1, len(res.home2work.distanceAVG) * 2 + 2, 2)
            )
            res.work2home.reqID = list(
                range(2, len(res.home2work.distanceAVG) * 2 + 3, 2)
            )
            return res


def fetchData(PERSIST_MODE: str, sourcedata: str = "Output") -> ds.TravelStats:
    res = ds.TravelStats()
    if PERSIST_MODE.lower() == "csv":
        res.loadH2WFromCSV(sourcedata + "_h2w.csv")
        res.loadW2FFromCSV(sourcedata + "_w2h.csv")
        res.home2work.reqID = list(range(1, len(res.home2work.distanceAVG) * 2 + 2, 2))
        res.work2home.reqID = list(range(2, len(res.home2work.distanceAVG) * 2 + 3, 2))
    elif PERSIST_MODE.lower() == "db":
        res.loadH2WFromDB()
        res.loadW2HFromDB()
    return res


def sendRequest(
    config: config.Config, request: requests.request, reqID: int
) -> requests.Response:
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
                sys.exit(1)

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
            sys.exit(1)

    return resp


def handleResponse(response: requests.Response) -> bool:
    if response.ok:
        elapsed = round(response.elapsed.microseconds / 1000, 1)
        logger.log(f"Request succeded, {elapsed} ms")
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


def buildJson(duration_in_traffic: int, duration: int, distance: int) -> dict:
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


def clearOldExportFiles(sourcedata: str) -> None:
    if os.path.exists(sourcedata + "_h2w.csv"):
        os.remove(sourcedata + "_h2w.csv")
    if os.path.exists(sourcedata + "_w2h.csv"):
        os.remove(sourcedata + "_w2h.csv")
