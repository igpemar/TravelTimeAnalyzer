import ETL.extract, ETL.transform, ETL.load
import datetime
import helpers.config, helpers.logger


def ETLPipeline(
    TravelStats: ETL.extract.TravelStats, config: helpers.config.Config
) -> None:
    lastDataDump = datetime.datetime.now()
    # Building request
    reqs = ETL.extract.GoogleMapsRequests()
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
            h2wResp = ETL.extract.sendRequest(config, reqs.h2wRequest, reqID_1)

            # Sending request for WORK2HOME
            helpers.logger.printRequestSent(reqID_2)
            w2hResp = ETL.extract.sendRequest(config, reqs.w2hRequest, reqID_2)

            # Parsing response
            h2wRespJSON = h2wResp.json()
            w2hRespJSON = w2hResp.json()

        else:
            # Parsing response
            helpers.logger.printRequestSent(reqID_1)
            h2wRespJSON = ETL.extract.mockh2wResponseAsJson()
            helpers.logger.printRequestSent(reqID_2)
            w2hRespJSON = ETL.extract.mockw2hResponseAsJson()

        # Storing data in memory
        ETL.transform.storeRespDataNP(TravelStats.home2work, reqTimestamp, h2wRespJSON)
        ETL.transform.storeRespDataNP(TravelStats.work2home, reqTimestamp, w2hRespJSON)

        # Persisting data in disk
        timeSinceLastDataDump = reqTimestamp - lastDataDump
        if reqID_1 == 1 or helpers.config.isItTimeToDumpData(
            timeSinceLastDataDump, config
        ):
            ETL.load.saveTravelStats2txt(TravelStats)
            lastDataDump = datetime.datetime.now()

        # Incrementing request numbers
        TravelStats.incrementRequestIDs(2)

        helpers.config.waitForNextCycle(reqTimestamp, config)
    return
