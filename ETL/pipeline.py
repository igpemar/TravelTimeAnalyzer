import os
import psutil
import datetime
import helpers.config
import ETL.extract as extract
import ETL.transform as transform
import ETL.load as load
import helpers.logger as logger


def ETLPipeline(TravelStats: extract.TravelStats, config) -> None:
    lastDataDump = datetime.datetime.now()
    # Building request
    reqs = extract.GoogleMapsRequests()
    reqs.build_request(config)
    while True:
        # Dealing with timestamps
        reqTimestamp = datetime.datetime.now()

        # Sending Requests
        reqID_1 = TravelStats.home2work.reqID[-1]
        reqID_2 = TravelStats.work2home.reqID[-1]
        if config.REQ_SEND == 1:
            # Sending request for HOME2WORK
            helpers.logger.printRequestSent(reqID_1)
            h2wResp = extract.sendRequest(config, reqs.h2wRequest, reqID_1)

            # Sending request for WORK2HOME
            helpers.logger.printRequestSent(reqID_2)
            w2hResp = extract.sendRequest(config, reqs.w2hRequest, reqID_2)

            # Parsing response
            h2wRespJSON = h2wResp.json()
            w2hRespJSON = w2hResp.json()

        else:
            # Parsing response
            helpers.logger.printRequestSent(reqID_1)
            h2wRespJSON = extract.mockh2wResponseAsJson()
            helpers.logger.printRequestSent(reqID_2)
            w2hRespJSON = extract.mockw2hResponseAsJson()

        # Storing data in memory
        transform.storeRespDataNP(TravelStats.home2work, reqTimestamp, h2wRespJSON)
        transform.storeRespDataNP(TravelStats.work2home, reqTimestamp, w2hRespJSON)

        # Persisting data in disk
        timeSinceLastDataDump = reqTimestamp - lastDataDump
        if reqID_1 == 1 or helpers.config.config.isItTimeToDumpData(
            timeSinceLastDataDump, config
        ):
            load.saveTravelStats2txt(TravelStats)
            lastDataDump = datetime.datetime.now()
            TravelStats.flushStats()

        # Incrementing request numbers
        TravelStats.incrementRequestIDs(2)
        monitor_total_ram_usage_current_process()
        helpers.config.config.waitForNextCycle(reqTimestamp, config)


def monitor_total_ram_usage():
    ram_usage = psutil.virtual_memory()
    logger.log(f" RAM Usage: {ram_usage.used/1024/1024} MB")
    return


def monitor_total_ram_usage_current_process():
    process = psutil.Process(os.getpid())
    logger.log(
        str(datetime.datetime.now())[0:19]
        + f" ; RAM Usage: {process.memory_info().rss/1024/1024} MB"
    )  # in bytes
    return
