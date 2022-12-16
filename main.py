import sys
import requests
import numpy as np
import datetime
import time
import pandas
import helpers.config, helpers.printers
import ETL.extract, ETL.transform, ETL.load

REQ_SEND = 0
RESTART_INPUT = ""

if __name__ == "__main__":
    # Get configuration variables
    config = helpers.config.Config()
    config.initiateAPIkey()
    API_KEY = config.getApiKey()

    # Print intro message
    helpers.printers.printIntroMessage(config)

    # Checking for restart
    print("Checking for restart...")
    (TravelStats, Restart) = ETL.extract.restart_check(RESTART_INPUT)

    # Checking for start time
    while helpers.config.isItTimeToStart(config.START_TIME):
        helpers.printers.printWaitTimeMessage(config.START_TIME)
        time.sleep(15)

    # Initializing Variables
    if Restart == 1:
        MyList1, MyList2 = [], []

    t0, dtDataDump = datetime.datetime.now(), datetime.datetime.now()

    # Building request
    h2wRequest, w2hRequest = ETL.extract.build_request(config)

    prev_week = t0.isocalendar()[1]
    print("Starting now at: ", t0)

    # Entering request loop
    while True:
        # Dealing with timestamps
        reqTimestamp = datetime.datetime.now()
        Current_Week = reqTimestamp.isocalendar()[1]

        # Sending Requests
        payload, headers = {}, {}
        reqID_1 = TravelStats.home2work.reqID[-1]
        reqID_2 = TravelStats.work2home.reqID[-1]
        if REQ_SEND == 1:
            # Sending request for HOME2WORK
            helpers.printers.printRequestSent(reqID_1)
            h2wResp = ETL.extract.sendRequest(config, h2wRequest, reqID_1)

            # Sending request for WORK2HOME
            helpers.printers.printRequestSent(reqID_2)
            w2hResp = ETL.extract.sendRequest(config, w2hRequest, reqID_2)

            # Parsing response
            h2wRespJSON = h2wResp.json()
            w2hRespJSON = w2hResp.json()

        else:
            # Parsing response
            helpers.printers.printRequestSent(reqID_1)
            h2wRespJSON = ETL.extract.mockh2wResponseAsJson()
            helpers.printers.printRequestSent(reqID_2)
            w2hRespJSON = ETL.extract.mockw2hResponseAsJson()

        # Storing data in memory
        ETL.transform.storeRespDataNP(TravelStats.home2work, reqTimestamp, h2wRespJSON)
        ETL.transform.storeRespDataNP(TravelStats.work2home, reqTimestamp, w2hRespJSON)

        # Persisting data in disk
        timeSinceLastDataDump = reqTimestamp - dtDataDump
        if reqID_1 == 1 or helpers.config.isItTimeToDumpData(
            timeSinceLastDataDump, config
        ):
            ETL.load.saveTravelStats2txt(TravelStats)
            dtDataDump = datetime.datetime.now()

        # Incrementing request numbers
        TravelStats.incrementRequestIDs(2)

        helpers.config.waitForNextCycle(reqTimestamp, config)
