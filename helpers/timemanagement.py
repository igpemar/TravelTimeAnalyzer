import time
from datetime import datetime as datetime
from datetime import timedelta as timedelta
import helpers.config as config
import helpers.logger as logger


def isItTimeToStart(start_time: datetime) -> bool:
    return start_time - datetime.now() > timedelta(seconds=1)


def isItTimeToDumpData(timeSinceLastDataDump: datetime, config: config.Config) -> bool:
    return timeSinceLastDataDump >= timedelta(
        seconds=config.DATA_DUMP_FREQUENCY, microseconds=10
    )


def findwaittime(time: datetime, hdsf: int, ldsf: int) -> int:
    if time.weekday():
        h = time.hour
        if 5 <= h < 11 or 13 <= h < 19:
            return hdsf
    return ldsf


def waitForNextCycle(reqTimestamp: datetime, config: config.Config) -> None:
    wait_time = findwaittime(
        reqTimestamp, config.HIGH_SAMPLING_FREQUENCY, config.LOW_SAMPLING_FREQUENCY
    )
    logger.log("- Waiting " + str(wait_time) + " second(s) for next request cycle-")
    logger.log("----------------------------------------------")
    time.sleep(wait_time)


def waitForStartTime(config: config.Config) -> None:
    while isItTimeToStart(config.START_TIME):
        logger.logWaitTimeMessage(config.START_TIME)
        time.sleep(5)
