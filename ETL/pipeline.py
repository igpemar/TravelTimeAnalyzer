import os
import sys
import psutil
import ETL.load as load
import ETL.extract as extract
import helpers.config as config
import helpers.logger as logger
import ETL.transform as transform
import helpers.datastructures as ds
from datetime import datetime as datetime
import helpers.timeutils as timemngmt


def ETLPipeline(TravelStats: ds.TravelStats, config: config.Config) -> None:
    lastDataDump = datetime.now()
    # Building request
    reqs = ds.GoogleMapsRequests()
    reqs.build_request(config)
    while True:
        # Dealing with timestamps
        reqTimestamp = datetime.now()

        # Sending Requests
        reqID_1 = TravelStats.A2B.reqID[-1]
        reqID_2 = TravelStats.B2A.reqID[-1]

        if config.REQ_SEND == 1:
            # Sending request for A2B
            logger.logRequestSent(reqID_1)
            A2BResp = extract.sendRequest(config, reqs.A2BRequest, reqID_1)

            # Sending request for B2A
            logger.logRequestSent(reqID_2)
            B2AResp = extract.sendRequest(config, reqs.B2ARequest, reqID_2)

            # Parsing response
            A2BRespJSON = A2BResp.json()
            B2ARespJSON = B2AResp.json()

        else:
            # Parsing response
            logger.logRequestSent(reqID_1)
            A2BRespJSON = extract.mockA2BResponseAsJson()
            logger.logRequestSent(reqID_2)
            B2ARespJSON = extract.mockB2AResponseAsJson()

        # Storing data in memory

        transform.storeRespDataNP(TravelStats.A2B, reqTimestamp, A2BRespJSON)
        transform.storeRespDataNP(TravelStats.B2A, reqTimestamp, B2ARespJSON)

        # Persisting data in disk
        timeSinceLastDataDump = reqTimestamp - lastDataDump
        if reqID_1 == 1 or timemngmt.isItTimeToDumpData(timeSinceLastDataDump, config):
            if config.PERSIST_MODE.lower() == "csv":
                load.saveTravelStats2txt(TravelStats)
            elif config.PERSIST_MODE.lower() == "db":
                load.saveTravelStats2DB(TravelStats)
            lastDataDump = datetime.now()
            TravelStats.flushStats()

        # Incrementing request numbers
        TravelStats.incrementRequestIDs(2)
        monitor_total_ram_usage_current_process()
        if timemngmt.isItTimeToEnd(config.END_TIME):
            logger.log("End time reached, exiting.")
            sys.exit(0)
        timemngmt.waitForNextCycle(reqTimestamp, config)


def monitor_total_ram_usage_current_process() -> None:
    process = psutil.Process(os.getpid())
    logger.log(f"Current RAM Usage: {round(process.memory_info().rss/1024/1024,1)} MB")
