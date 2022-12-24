import os
import time
import threading
import numpy as np
from os.path import exists
from filelock import FileLock
import ETL.extract as extract
import helpers.logger as logger
import ETL.transform as transform


def saveTravelStats2txt(TravelStats: extract.TravelStats, dest: str = "Output") -> None:
    h2wData = transform.travelTimeColumnStack(TravelStats.home2work)
    w2hData = transform.travelTimeColumnStack(TravelStats.work2home)
    logger.log("--> Dumping response data to output file...")

    start_time = time.time()
    file_h2w = dest + "_h2w.csv"
    file_w2h = dest + "_w2h.csv"
    t1 = threading.Thread(target=writeDataToCsv, args=(file_h2w, h2wData))
    t2 = threading.Thread(target=writeDataToCsv, args=(file_w2h, w2hData))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    elapsed = time.time() - start_time

    logger.log(f"---> Done Writing! {round(elapsed*1000,2)} ms")
    logger.log(
        str(TravelStats.home2work.timestampSTR[-1])
        + " ; ----------------------------------------------"
    )


def writeDataToCsv(fileName: str, h2wData: np.ndarray) -> None:
    if exists(fileName):
        headers = ""
    else:
        headers = "Req #. ; Timestamp ; Distance [km] ; Duration (incl.traffic) [min] ; Duration (excl.traffic) [min]"

    locklock = FileLock(fileName + ".lock")

    with locklock.acquire(timeout=10):
        f = open(fileName, "a+")
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
        if os.path.exists(fileName + ".lock"):
            os.remove(fileName + ".lock")
