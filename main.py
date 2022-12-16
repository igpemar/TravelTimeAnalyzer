import sys
import requests
import numpy as np
import datetime
import time
import pandas
import helpers.config, helpers.printers
import ETL.extract, ETL.transform, ETL.load

REQ_SEND = 0

if __name__ == "__main__":
    # Get configuration variables
    config = helpers.config.Config()
    config.initiateAPIkey()
    API_KEY = config.getApiKey()

    # Print intro message
    helpers.printers.printIntroMessage(config)

    # Checking for restart
    print("Checking for restart...")
    (TravelStats, Restart) = ETL.extract.restart_check("")

    # Checking for start time
    while helpers.config.isItTimeToStart(config.START_TIME):
        helpers.printers.printWaitTimeMessage(config.START_TIME)
        time.sleep(15)

    # Initializing Variables
    if Restart == 1:
        MyList1, MyList2 = [], []

    (
        w_req_n_1,
        w_dt_str,
        w_1_d_i_t_1,
        w_2_d_i_t_2,
        w_1_d_avg_1,
        w_2_d_avg_2,
        w_1_dist_1,
        w_2_dist_2,
        dt,
    ) = ([], [], [], [], [], [], [], [], [])
    t0, dtDataDump = datetime.datetime.now(), datetime.datetime.now()

    # Building request
    h2wRequest, w2hRequest = ETL.extract.build_request(config)

    prev_week = t0.isocalendar()[1]
    print("Starting now at: ", t0)

    # Entering request loop
    while True:
        # Dealing with timestamps
        reqTimestamp = datetime.datetime.now()
        dt.append(reqTimestamp)
        Current_Week = reqTimestamp.isocalendar()[1]

        # Sending Requests
        payload, headers = {}, {}
        reqID_1 = TravelStats.home2work.reqID[-1]
        reqID_2 = TravelStats.work2home.reqID[-1]
        if REQ_SEND == 1:
            # Request for HOME2WORK
            helpers.printers.printRequestSent(reqID_1)
            h2wResp = ETL.extract.sendRequest(config, h2wRequest, reqID_1)

            # Request for WORK2HOME
            helpers.printers.printRequestSent(reqID_2)
            w2hResp = ETL.extract.sendRequest(config, w2hRequest, reqID_2)

            # Store Data
            TravelStats.setTimestamp(reqTimestamp)

            print(str(reqTimestamp)[0:-7] + " ; Storing data")

            h2wRespJSON = h2wResp.json()
            w2hRespJSON = w2hResp.json()
            # Incrementing request numbers

        else:
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
        TravelStats.incrementRequestIDs(2)
        helpers.config.waitForNextCycle(reqTimestamp, config)
