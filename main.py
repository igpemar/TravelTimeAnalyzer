import sys
import requests
import numpy as np
import datetime
import time
import pandas


def findwaittime(current_time, hdsf, ldsf):
    wait = ldsf
    if current_time.weekday():
        h = current_time.hour
        if 5 <= h < 11 or 13 <= h < 19:
            wait = hdsf

    return wait


def restart_check():
    while True:
        s = input(
            "Would you like to start from scratch and erase the existing data? Y/N/A "
        )
        req_n_1, req_n_2, dt_str, d_i_t_1, d_i_t_2, d_avg_1, d_avg_2, dist_1, dist_2 = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )
        if s == "A" or s == "A":
            sys.exit()
        elif s == "y" or s == "Y":
            Restart_Flag = 1
            return (
                req_n_1,
                req_n_2,
                dt_str,
                d_i_t_1,
                d_i_t_2,
                d_avg_1,
                d_avg_2,
                dist_1,
                dist_2,
                Restart_Flag,
            )
        elif s == "n" or s == "N":
            Restart_Flag = 0
            try:
                Output_1 = pandas.read_csv("Output_1.csv", sep=";")
                Output_2 = pandas.read_csv("Output_2.csv", sep=";")
            except:
                print(
                    "No data files were found, impossible to restart from existing data, exiting ..."
                )
                sys.exit()

            for i in range(Output_1.shape[0]):
                req_n_1.append(Output_1.values[i][0])
                dt_str.append(Output_1.values[i][1].strip())
                dist_1.append(Output_1.values[i][2])
                d_avg_1.append(Output_1.values[i][3])
                d_i_t_1.append(Output_1.values[i][4])

            for i in range(Output_2.shape[0]):
                req_n_2.append(Output_2.values[i][0])
                dist_2.append(Output_2.values[i][2])
                d_avg_2.append(Output_2.values[i][3])
                d_i_t_2.append(Output_2.values[i][4])

            return (
                req_n_1,
                dt_str,
                dist_1,
                d_avg_1,
                d_i_t_1,
                req_n_2,
                dist_2,
                d_avg_2,
                d_i_t_2,
                Restart_Flag,
            )


def intro_message(HOME, WORK):
    print(
        "-----------------------------------------------------------------------------"
    )
    print("  Welcome to Google Maps Commute Analyzer")
    print(
        "------------------------------------------------------------------------------"
    )
    print(
        " Fetching driving time from " + str(HOME[0]) + " N ; " + str(HOME[1]) + " E "
    )
    print(" to " + str(WORK[0]) + " N ; " + str(WORK[1]) + " E.")
    print(
        "------------------------------------------------------------------------------"
    )
    print("Starting")
    print(" ")


def build_request(HOME, WORK, API_KEY):
    outputFormat = "json"
    RequestStart = "https://maps.googleapis.com/maps/api/distancematrix/"
    Origin = str(HOME[0]) + "%2C" + str(HOME[1])
    Destination = str(WORK[0]) + "%2C" + str(WORK[1])
    Req_car_Home_To_work = (
        RequestStart
        + outputFormat
        + "?destinations="
        + Destination
        + "&origins="
        + Origin
        + "&mode=driving"
        + "&departure_time=now"
        + "&key="
        + API_KEY
    )
    Req_car_Work_To_Home = (
        RequestStart
        + outputFormat
        + "?destinations="
        + Origin
        + "&origins="
        + Destination
        + "&mode=driving"
        + "&departure_time=now"
        + "&key="
        + API_KEY
    )

    return Req_car_Home_To_work, Req_car_Work_To_Home


HOME = (55.688519, 12.528168)  # GPS Coordinates in decimal degrees DDD.DDDDD
WORK = (55.672162, 12.585666)  # GPS Coordinates in decimal degrees DDD.DDDDD
API_KEY = "AIzaSyC2FhCdJDamyyjhTxRS0qKJfN220C0rB-w"  # Google Api Key

DATA_DUMP_FREQUENCY = 10  # In seconds (integer)
HIGH_SAMPLING_FREQUENCY = 1  # In seconds Integer
LOW_SAMPLING_FREQUENCY = 1200  # In Seconds Integer

Req_send = 1

Start_Time = datetime.datetime(
    2022, 12, 11, 19, 25, 0
)  # Start time of the code (year, month, day, hour, minute, second)
# WARNING: DO NOT USE LEADING ZEROS

# Intro message
intro_message(HOME, WORK)

# Checking for restart
(
    req_n_1,
    dt_str,
    dist_1,
    d_avg_1,
    d_i_t_1,
    req_n_2,
    dist_2,
    d_avg_2,
    d_i_t_2,
    Restart_Flag,
) = restart_check()

# Checking for start time
while Start_Time - datetime.datetime.now() > datetime.timedelta(seconds=1):
    print(str(datetime.datetime.now()) + "  ; Waiting for Startime " + str(Start_Time))
    time.sleep(30)

# Initializing Variables

if Restart_Flag == 1:
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
Req_1, Req_2 = build_request(HOME, WORK, API_KEY)

prev_week = t0.isocalendar()[1]

print("Start time: ", t0)

# Entering request loop
while 1:
    # Incrementing request number
    if not req_n_1:
        req_n_1, req_n_2 = [1], [2]
    else:
        req_n_1.append(req_n_1[-1] + 2)
        req_n_2.append(req_n_2[-1] + 2)

    # Dealing with timestamps
    dt_req = datetime.datetime.now()
    dt.append(dt_req)

    dt_str.append(
        str(dt[-1].year)
        + "-"
        + f"{dt[-1].month:02}"
        + "-"
        + f"{dt[-1].day:02}"
        + " "
        + f"{dt[-1].hour:02}"
        + ":"
        + f"{dt[-1].minute:02}"
        + ":"
        + f"{dt[-1].second:02}"
    )
    print(dt_str[-1])
    Current_Week = dt_req.isocalendar()[1]

    # Sending Requests
    try:
        if Req_send == 1:
            payload, headers = {}, {}

            print(str(dt_req)[0:-7] + " ; Sending request #" + str(req_n_1[-1]))
            response_1 = requests.request("GET", Req_1, headers=headers, data=payload)

            print(str(dt_req)[0:-7] + " ; Request response successfully received")
            print(str(dt_req)[0:-7] + " ; Sending request #" + str(req_n_2[-1]))

            response_2 = requests.request("GET", Req_2, headers=headers, data=payload)

            print(str(dt_req)[0:-7] + " ; Request response successfully received")
            print(str(dt_req)[0:-7] + " ; Storing data")
        else:
            response_1, response_2 = "", ""
    except:
        req_n_1[-1] = req_n_1[-1] - 2
        req_n_2[-1] = req_n_2[-1] - 2
        print(
            "ERROR: An error occurred while performing the API requests, check your internet connection"
        )
        print("waiting 60 seconds before trying again")
        time.sleep(60)
        continue

    if Current_Week != prev_week and Req_send == 1:
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
    if Req_send == 1:
        A = response_1.json()

        w_req_n_1.append(req_n_1[-1])
        w_dt_str.append(dt_str[-1])
        w_1_d_i_t_1.append(
            round(A["rows"][0]["elements"][0]["duration_in_traffic"]["value"] / 60.0, 2)
        )
        w_1_d_avg_1.append(
            round(A["rows"][0]["elements"][0]["duration"]["value"] / 60.0, 2)
        )
        w_1_dist_1.append(
            round(A["rows"][0]["elements"][0]["distance"]["value"] / 1000.0, 2)
        )

        d_i_t_1.append(
            round(A["rows"][0]["elements"][0]["duration_in_traffic"]["value"] / 60.0, 2)
        )
        d_avg_1.append(
            round(A["rows"][0]["elements"][0]["duration"]["value"] / 60.0, 2)
        )
        dist_1.append(
            round(A["rows"][0]["elements"][0]["distance"]["value"] / 1000.0, 2)
        )
        MyList1 = np.column_stack((req_n_1, dt_str, dist_1, d_avg_1, d_i_t_1))

        B = response_2.json()

        w_2_d_i_t_2.append(
            round(B["rows"][0]["elements"][0]["duration_in_traffic"]["value"] / 60.0, 2)
        )
        w_2_d_avg_2.append(
            round(B["rows"][0]["elements"][0]["duration"]["value"] / 60.0, 2)
        )
        w_2_dist_2.append(
            round(B["rows"][0]["elements"][0]["distance"]["value"] / 1000.0, 2)
        )

        d_i_t_2.append(
            round(B["rows"][0]["elements"][0]["duration_in_traffic"]["value"] / 60.0, 2)
        )
        d_avg_2.append(
            round(B["rows"][0]["elements"][0]["duration"]["value"] / 60.0, 2)
        )
        dist_2.append(
            round(B["rows"][0]["elements"][0]["distance"]["value"] / 1000.0, 2)
        )
        MyList2 = np.column_stack((req_n_2, dt_str, dist_2, d_avg_2, d_i_t_2))

        Elapsed_Time_Since_Last_Data_Dump = dt_req - dt_data_dump
        if req_n_1[-1] == 1 or Elapsed_Time_Since_Last_Data_Dump >= datetime.timedelta(
            seconds=DATA_DUMP_FREQUENCY, microseconds=10
        ):
            print(str(dt_req)[0:-7] + " ; Writing request data to output file")
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

    print(str(dt_req)[0:-7] + " ; ---> DONE")
    print(str(dt_req)[0:-7] + " ; ----------------------------------------------")
    wait_time = findwaittime(dt_req, HIGH_SAMPLING_FREQUENCY, LOW_SAMPLING_FREQUENCY)
    print(
        str(dt_req)[0:-7] + " ; ----- Waiting " + str(wait_time) + " seconds.-----"
    )  #
    print(str(dt_req)[0:-7] + " ; ----------------------------------------------")
    time.sleep(wait_time)
