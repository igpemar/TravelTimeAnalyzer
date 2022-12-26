import time
import helpers.config as config
import helpers.logger as logger
from datetime import datetime as datetime
from datetime import timedelta as timedelta


def isItTimeToStart(start_time: datetime) -> bool:
    return start_time - datetime.now() > timedelta(seconds=1)


def isItTimeToEnd(end_time: datetime) -> bool:
    if end_time == "":
        return False
    return end_time - datetime.now() < timedelta(seconds=1)


def isItTimeToDumpData(timeSinceLastDataDump: datetime, config: config.Config) -> bool:
    return timeSinceLastDataDump >= timedelta(
        seconds=config.DATA_DUMP_INTERVAL, microseconds=10
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
    runTimeSeconds = (datetime.now() - reqTimestamp).total_seconds()
    logger.log("- Waiting " + str(wait_time) + " second(s) for next request cycle-")
    logger.log("------------------------------------------------")
    if wait_time > runTimeSeconds:
        time.sleep(wait_time - runTimeSeconds)


def waitForStartTime(config: config.Config) -> None:
    while isItTimeToStart(config.START_TIME):
        logger.logWaitTimeMessage(config.START_TIME)
        time.sleep(5)
