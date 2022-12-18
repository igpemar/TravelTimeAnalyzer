import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time
import pandas
import datetime
import seaborn as sns

axis_mode = "Running"  # Choose between "Running", "FullWeek" and "FullDay"

DISPLAY_IMAGE = True
SAVE_IMAGE = True
SAVE_LOCATION = "Plot.jgp"


def initialize_plot_axes(
    range="",
    XLABEL="X label",
    XLABFS=15,
    YLABEL="Y label",
    YLABFS=15,
    XTICKFS=10,
    YTICKFS=10,
):

    # Plotting the dataset
    # sns.set()
    if range != "":
        plt.axis(range)
    plt.xticks(fontsize=XTICKFS)
    plt.yticks(fontsize=YTICKFS)
    plt.xlabel(XLABEL, fontsize=XLABFS)
    plt.ylabel(YLABEL, fontsize=YLABFS)


def restart_check(DataFolderPath="", Filename="Output"):
    reqID_1, reqID_2, reqTsStr, d_i_t_1, d_i_t_2, d_avg_1, d_avg_2, dist_1, dist_2 = (
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
    if DataFolderPath:
        if DataFolderPath[-1] != "/":
            DataFolderPath += "/"
    try:
        Output_1 = pandas.read_csv(DataFolderPath + Filename + "_h2w.csv", sep=";")
        Output_2 = pandas.read_csv(DataFolderPath + Filename + "_w2h.csv", sep=";")
    except pandas.errors.EmptyDataError:
        return [], [], [], [], [], [], []

    for i in range(Output_1.shape[0]):
        reqID_1.append(Output_1.values[i][0])
        reqTsStr.append(Output_1.values[i][1].strip())
        dist_1.append(Output_1.values[i][2])
        d_avg_1.append(Output_1.values[i][4])
        d_i_t_1.append(Output_1.values[i][3])

    for i in range(Output_2.shape[0]):
        reqID_2.append(Output_2.values[i][0])
        dist_2.append(Output_2.values[i][2])
        d_avg_2.append(Output_2.values[i][4])
        d_i_t_2.append(Output_2.values[i][3])

    reqs = np.column_stack((reqID_1, reqID_2))
    dist = np.column_stack((dist_1, dist_2))
    d_avg = np.column_stack((d_avg_1, d_avg_2))
    d_i_t = np.column_stack((d_i_t_1, d_i_t_2))

    datevec, elapsed_time = [], []
    try:
        [
            datevec.append(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S"))
            for date in reqTsStr
        ]
    except:
        [
            datevec.append(datetime.datetime.strptime(date, "%d-%b-%Y %H:%M:%S"))
            for date in reqTsStr
        ]
    datevec = np.array(datevec).reshape(-1, 1)

    [elapsed_time.append(t - datevec[0]) for t in datevec]

    elapsed_time = np.array(elapsed_time).reshape(-1, 1)
    elapsed_time_sec = np.array(
        [
            elapsed_time[i][0].days * 24 * 3600 + elapsed_time[i][0].seconds
            for i in range(elapsed_time.shape[0])
        ]
    ).reshape(-1, 1)
    return reqs, reqTsStr, datevec, elapsed_time_sec, dist, d_avg, d_i_t


def postProcess(
    DISPLAY_IMAGE=True, SAVE_IMAGE=False, SAVE_LOCATION="Plot.jgp", sampling=0
):
    while True:
        # Reading the data
        reqs, dt_str, datevec, elapsed_time_sec, dist, d_avg, d_i_t = restart_check()
        if reqs == []:
            continue
        if not DISPLAY_IMAGE:
            matplotlib.use("agg")
        # Plotting
        # sns.set()
        if DISPLAY_IMAGE:
            plt.close(1)
        plt.figure(1, figsize=(15, 5))
        if len(elapsed_time_sec <= 1):
            Axis_Range = ""
        else:
            Axis_Range = [
                elapsed_time_sec[0],
                elapsed_time_sec[-1],
                0,
                40,
            ]
        initialize_plot_axes(
            range=Axis_Range,
            XLABEL="Elapsed Time [s]",
            XLABFS=15,
            YLABEL="Comute Time  [min]",
            YLABFS=15,
            XTICKFS=10,
            YTICKFS=10,
        )
        X = elapsed_time_sec - elapsed_time_sec[0]
        Y = d_i_t[:, 0].reshape(-1, 1)
        plt.plot(X, Y, "b.")

        Y = d_i_t[:, 1].reshape(-1, 1)
        plt.plot(X, Y, "r.")

        t0 = datevec[0][0]
        if axis_mode == "FullWeek":
            labels = [
                str(
                    (
                        t0
                        + datetime.timedelta(
                            hours=int(i), minutes=-t0.minute, seconds=-t0.second
                        )
                    )
                )[:-3]
                for i in range(0, 7 * 24 + 8, 8)
            ]
            plt.xticks(
                np.linspace(0, 60 * 60 * 24 * 7, len(range(0, 7 * 24 + 8, 8))),
                labels=labels,
            )
        elif axis_mode == "FullDay":
            labels = [
                str(
                    (
                        t0
                        + datetime.timedelta(
                            hours=int(i), minutes=-t0.minute, seconds=-t0.second
                        )
                    )
                )[:-3]
                for i in range(0, 1 * 24 + 1, 1)
            ]
            xticks = np.linspace(0, 60 * 60 * 24, len(range(0, 1 * 24 + 1, 1)))
            plt.xticks(xticks, labels=labels)

        plt.xticks(rotation=45)
        plt.grid()
        plt.tight_layout()
        if DISPLAY_IMAGE:
            plt.show()

        if SAVE_IMAGE:
            plt.savefig(SAVE_LOCATION)

        if sampling > 0:
            time.sleep(sampling)
        else:
            break
