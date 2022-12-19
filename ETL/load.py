import numpy as np
import ETL.transform, ETL.extract


def saveTravelStats2txt(
    TravelStats: ETL.extract.TravelStats, destination: str = "Output"
):
    MyList1 = ETL.transform.travelTimeColumnStack(TravelStats.home2work)
    MyList2 = ETL.transform.travelTimeColumnStack(TravelStats.work2home)
    print(
        TravelStats.home2work.timestampSTR[-1]
        + " ; --> Dumping response data to output file..."
    )
    np.savetxt(
        destination + "_h2w.csv",
        MyList1,
        fmt="%s",
        delimiter=" ; ",
        comments="",
        header="Req #. ; Timestamp ; Distance [km] ; Duration (incl.traffic) [min] ; Duration (excl.traffic) [min]",
    )
    np.savetxt(
        destination + "_w2h.csv",
        MyList2,
        fmt="%s",
        delimiter=" ; ",
        comments="",
        header="Req #. ; Timestamp ; Distance [km] ; Duration (incl.traffic) [min] ; Duration (excl.traffic) [min]",
    )
    print(TravelStats.home2work.timestampSTR[-1] + " ; ---> DONE!")
    print(
        str(TravelStats.home2work.timestampSTR[-1])
        + " ; ----------------------------------------------"
    )
