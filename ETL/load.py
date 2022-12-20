import os
import numpy as np
import ETL.transform, ETL.extract
from os.path import exists
from filelock import FileLock


def saveTravelStats2txt(
    TravelStats: ETL.extract.TravelStats, destination: str = "Output"
):
    h2wData = ETL.transform.travelTimeColumnStack(TravelStats.home2work)
    w2hData = ETL.transform.travelTimeColumnStack(TravelStats.work2home)
    print(
        TravelStats.home2work.timestampSTR[-1]
        + " ; --> Dumping response data to output file..."
    )

    file = destination + "_h2w.csv"
    writeDataToCsv(file, h2wData)
    file = destination + "_w2h.csv"
    writeDataToCsv(file, w2hData)

    print(TravelStats.home2work.timestampSTR[-1] + " ; ---> Done Writing!")
    print(
        str(TravelStats.home2work.timestampSTR[-1])
        + " ; ----------------------------------------------"
    )


def writeDataToCsv(file, h2wData):
    if exists(file):
        headers = ""
    else:
        headers = "Req #. ; Timestamp ; Distance [km] ; Duration (incl.traffic) [min] ; Duration (excl.traffic) [min]"

    locklock = FileLock(file + ".lock")

    with locklock.acquire(timeout=10):
        f = open(file, "a+")
        np.savetxt(
            f,
            h2wData,
            fmt="%s",
            delimiter=" ; ",
            comments="",
            header=headers,
        )
        locklock.release()
        f.close()
        if os.path.exists(file + ".lock"):
            os.remove(file + ".lock")
