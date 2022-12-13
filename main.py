import sys
import requests
import numpy as np
import datetime
import time
import pandas
import helpers.config, helpers.printers
import ETL.extract

REQ_SEND = 1


def findwaittime(current_time, hdsf, ldsf):
    wait = ldsf
    if current_time.weekday():
        h = current_time.hour
        if 5 <= h < 11 or 13 <= h < 19:
            wait = hdsf

    return wait


# Start time of the code (year, month, day, hour, minute, second)
# WARNING: DO NOT USE LEADING ZEROS
if __name__ == "__main__":
    # Get configuration variables
    config = helpers.config.Config()
    config.initiateAPIkey()
    API_KEY = config.getApiKey()

    # Print intro message
    helpers.printers.printIntroMessage(config)

    # Checking for restart
    print("Checking for restart...")
    (TravelTime, Restart) = ETL.extract.restart_check()

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
    t0, dt_data_dump = datetime.datetime.now(), datetime.datetime.now()

    # Building request
    h2wRequest, w2hRequest = ETL.extract.build_request(config)

    prev_week = t0.isocalendar()[1]
    print("Starting now at: ", t0)

    # Entering request loop
    while True:
        # Incrementing request numbers
        TravelTime.incrementRequestIDs(2)

        # Dealing with timestamps
        reqTimestamp = datetime.datetime.now()
        print(reqTimestamp)
        dt.append(reqTimestamp)
        Current_Week = reqTimestamp.isocalendar()[1]

        # Sending Requests
        if REQ_SEND == 1:
            payload, headers = {}, {}

            helpers.printers.printRequestSent(TravelTime.home2work.reqID[-1])
            h2wResp = requests.request("GET", h2wRequest, headers=headers, data=payload)
            ok = ETL.extract.handleResponse(h2wResp)
            if not ok:
                TravelTime.home2work.reqID -= 1
                time.sleep(60)
                continue

            helpers.printers.printRequestSent(TravelTime.work2home.reqID[-1])
            w2hResp = requests.request("GET", w2hRequest, headers=headers, data=payload)
            ok = ETL.extract.handleResponse(w2hResp)
            if not ok:
                TravelTime.work2home.reqID -= 1
                time.sleep(60)
                continue
            TravelTime.setTimestamp(reqTimestamp)
            print(str(reqTimestamp)[0:-7] + " ; Storing data")
        else:
            h2wResp, w2hResp = "", ""

        if Current_Week != prev_week and REQ_SEND == 1:
            This_Week_1 = np.column_stack(
                (w_req_n_1, w_dt_str, w_1_dist_1, w_1_d_avg_1, w_1_d_i_t_1)
            )
            This_Week_2 = np.column_stack(
                (w_req_n_1, w_dt_str, w_2_dist_2, w_2_d_avg_2, w_2_d_i_t_2)
            )

            np.savetxt(
                "Week_" + f"{prev_week:02}" + "_Output_1.csv",
                This_Week_1,
                fmt="%s",
                delimiter=" ; ",
                comments="",
                header="Req nbr. ; Timestamp ; Distance [km] ; Duration (incl.traffic) [min] ; Duration (excl.traffic) [min]",
            )
            np.savetxt(
                "Week_" + f"{prev_week:02}" + "_Output_2.csv",
                This_Week_1,
                fmt="%s",
                delimiter=" ; ",
                comments="",
                header="Req nbr. ; Timestamp ; Distance [km] ; Duration (incl.traffic) [min] ; Duration (excl.traffic) [min]",
            )
            prev_week = Current_Week
            (
                w_req_n_1,
                w_dt_str,
                w_1_d_i_t_1,
                w_2_d_i_t_2,
                w_1_d_avg_1,
                w_2_d_avg_2,
                w_1_dist_1,
                w_2_dist_2,
            ) = ([], [], [], [], [], [], [], [])

        # Storing Data
        if REQ_SEND == 1:
            A = h2wResp.json()

            w_req_n_1.append(TravelTime.home2work.reqID[-1])
            w_dt_str.append(dt_str[-1])
            w_1_d_i_t_1.append(
                round(
                    A["rows"][0]["elements"][0]["duration_in_traffic"]["value"] / 60.0,
                    2,
                )
            )
            w_1_d_avg_1.append(
                round(A["rows"][0]["elements"][0]["duration"]["value"] / 60.0, 2)
            )
            w_1_dist_1.append(
                round(A["rows"][0]["elements"][0]["distance"]["value"] / 1000.0, 2)
            )

            d_i_t_1.append(
                round(
                    A["rows"][0]["elements"][0]["duration_in_traffic"]["value"] / 60.0,
                    2,
                )
            )
            d_avg_1.append(
                round(A["rows"][0]["elements"][0]["duration"]["value"] / 60.0, 2)
            )
            dist_1.append(
                round(A["rows"][0]["elements"][0]["distance"]["value"] / 1000.0, 2)
            )
            MyList1 = np.column_stack(
                (TravelTime.home2work.reqID, dt_str, dist_1, d_avg_1, d_i_t_1)
            )

            B = w2hResp.json()

            w_2_d_i_t_2.append(
                round(
                    B["rows"][0]["elements"][0]["duration_in_traffic"]["value"] / 60.0,
                    2,
                )
            )
            w_2_d_avg_2.append(
                round(B["rows"][0]["elements"][0]["duration"]["value"] / 60.0, 2)
            )
            w_2_dist_2.append(
                round(B["rows"][0]["elements"][0]["distance"]["value"] / 1000.0, 2)
            )

            d_i_t_2.append(
                round(
                    B["rows"][0]["elements"][0]["duration_in_traffic"]["value"] / 60.0,
                    2,
                )
            )
            d_avg_2.append(
                round(B["rows"][0]["elements"][0]["duration"]["value"] / 60.0, 2)
            )
            dist_2.append(
                round(B["rows"][0]["elements"][0]["distance"]["value"] / 1000.0, 2)
            )
            MyList2 = np.column_stack(
                (TravelTime.work2home.reqID, dt_str, dist_2, d_avg_2, d_i_t_2)
            )

            Elapsed_Time_Since_Last_Data_Dump = reqTimestamp - dt_data_dump
            if TravelTime.home2work.reqID[
                -1
            ] == 1 or Elapsed_Time_Since_Last_Data_Dump >= datetime.timedelta(
                seconds=DATA_DUMP_FREQUENCY, microseconds=10
            ):
                print(
                    str(reqTimestamp)[0:-7] + " ; Writing request data to output file"
                )
                np.savetxt(
                    "Output_1.csv",
                    MyList1,
                    fmt="%s",
                    delimiter=" ; ",
                    comments="",
                    header="Req nbr. ; Timestamp ; Distance [km] ; Duration (incl.traffic) [min] ; Duration (excl.traffic) [min]",
                )
                np.savetxt(
                    "Output_2.csv",
                    MyList2,
                    fmt="%s",
                    delimiter=" ; ",
                    comments="",
                    header="Req nbr. ; Timestamp ; Distance [km] ; Duration (incl.traffic) [min] ; Duration (excl.traffic) [min]",
                )
                dt_data_dump = datetime.datetime.now()

        else:
            MyList1, MyList2 = [], []

        print(str(reqTimestamp)[0:-7] + " ; ---> DONE")
        print(
            str(reqTimestamp)[0:-7]
            + " ; ----------------------------------------------"
        )
        wait_time = findwaittime(
            reqTimestamp, HIGH_SAMPLING_FREQUENCY, LOW_SAMPLING_FREQUENCY
        )
        print(
            str(reqTimestamp)[0:-7]
            + " ; ----- Waiting "
            + str(wait_time)
            + " seconds.-----"
        )  #
        print(
            str(reqTimestamp)[0:-7]
            + " ; ----------------------------------------------"
        )
        time.sleep(wait_time)
