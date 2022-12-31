import os
import time
import threading
import numpy as np
from os.path import exists
from filelock import FileLock
import helpers.logger as logger
import helpers.config as config
import ETL.transform as transform
import helpers.datastructures as ds


def saveTravelStats2txt(
    config: config.Config, TravelStats: ds.TravelStats, dest: str = "Output"
) -> None:
    A2BData = transform.travelTimeColumnStack(TravelStats.A2B)
    if config.RETURNMODE:
        B2AData = transform.travelTimeColumnStack(TravelStats.B2A)
    logger.log("--> Dumping response data to output file...")

    start = time.time()
    file_A2B = dest + "_A2B.csv"
    t1 = threading.Thread(target=writeDataToCsv, args=(file_A2B, A2BData))
    t1.start()
    t1.join()
    if config.RETURNMODE:
        file_B2A = dest + "_B2A.csv"
        t2 = threading.Thread(target=writeDataToCsv, args=(file_B2A, B2AData))
        t2.start()
        t2.join()
    elapsed = time.time() - start

    logger.log(f"---> Done Writing! {round(elapsed*1000,2)} ms")
    logger.log("------------------------------------------------")


def saveTravelStats2DB(config: config.Config, TravelStats: ds.TravelStats) -> None:
    dbConfig = db.getDBConfig()
    conn = db.connect2DB(dbConfig)
    data = TravelStats.A2B
    for i, _ in enumerate(data.reqID):
        row = [
            data.reqID[i],
            data.timestampSTR[i],
            data.distanceAVG[i],
            data.durationInclTraffic[i],
            data.durationEnclTraffic[i],
        ]
        db.persistRow(conn, "A2B", row)
    if config.RETURNMODE:
        data = TravelStats.B2A
        for i, _ in enumerate(data.reqID):
            row = [
                data.reqID[i],
                data.timestampSTR[i],
                data.distanceAVG[i],
                data.durationInclTraffic[i],
                data.durationEnclTraffic[i],
            ]
            db.persistRow(conn, "B2A", row)
    logger.log("Data persisted successfully in database tables")
    db.closeDBconnection(conn)


def writeDataToCsv(fileName: str, Data: np.ndarray) -> None:
    if exists(fileName):
        headers = ""
    else:
        headers = "Req #. ; Timestamp ; Distance [km] ; Duration (incl.traffic) [min] ; Duration (excl.traffic) [min]"

    locklock = FileLock(fileName + ".lock")

    with locklock.acquire(timeout=10):
        f = open(fileName, "a+")
        np.savetxt(
            f,
            Data,
            fmt="%s",
            delimiter=" ; ",
            comments="",
            header=headers,
        )
        locklock.release()
        f.close()
        if os.path.exists(fileName + ".lock"):
            os.remove(fileName + ".lock")
