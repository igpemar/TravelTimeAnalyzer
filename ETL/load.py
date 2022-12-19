import numpy as np
import ETL.transform, ETL.extract
from os.path import exists


def saveTravelStats2txt(
    TravelStats: ETL.extract.TravelStats, destination: str = "Output"
):
    h2wData = ETL.transform.travelTimeColumnStack(TravelStats.home2work)
    w2hData = ETL.transform.travelTimeColumnStack(TravelStats.work2home)
    print(
        TravelStats.home2work.timestampSTR[-1]
        + " ; --> Dumping response data to output file..."
    )
    path_to_file = destination + "_h2w.csv"
    if exists(path_to_file):
        headers = ""
    else:
        headers = "Req #. ; Timestamp ; Distance [km] ; Duration (incl.traffic) [min] ; Duration (excl.traffic) [min]"
    with open(path_to_file, "a") as f:
        np.savetxt(
            f,
            h2wData,
            fmt="%s",
            delimiter=" ; ",
            comments="",
            header=headers,
        )

    path_to_file = destination + "_w2h.csv"
    if exists(path_to_file):
        headers = ""
    else:
        headers = "Req #. ; Timestamp ; Distance [km] ; Duration (incl.traffic) [min] ; Duration (excl.traffic) [min]"
    with open(path_to_file, "a") as g:
        np.savetxt(
            g,
            w2hData,
            fmt="%s",
            delimiter=" ; ",
            comments="",
            header=headers,
        )
    print(TravelStats.home2work.timestampSTR[-1] + " ; ---> DONE!")
    print(
        str(TravelStats.home2work.timestampSTR[-1])
        + " ; ----------------------------------------------"
    )
