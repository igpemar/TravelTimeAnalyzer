from datetime import datetime as datetime


def logIntroMessage(home: tuple, work: tuple) -> None:
    homeCardinalLat = " N ; "
    workCardinalLat = " N ; "
    if home[0] < 0:
        homeCardinalLat = " S ; "
    if work[0] < 0:
        workCardinalLat = " S ; "

    homeCardinalLon = " E "
    workCardinalLon = " E "
    if home[0] < 0:
        homeCardinalLon = " W "
    if work[0] < 0:
        workCardinalLon = " W "

    print("")
    print(
        "-----------------------------------------------------------------------------"
    )
    print("  Welcome to Google Maps Commute Analyzer")
    print(
        "------------------------------------------------------------------------------"
    )
    print("Fetching driving time")
    print(" from:")
    print("   " + str(home[0]) + homeCardinalLat + str(home[1]) + homeCardinalLon)
    print(" to:")
    print("   " + str(work[0]) + workCardinalLat + str(work[1]) + workCardinalLon)
    print(
        "------------------------------------------------------------------------------"
    )


def logWaitTimeMessage(start_time: str) -> None:
    log(
        "Current time: "
        + str(datetime.now())
        + "  ; Waiting for Startime ... "
        + str(start_time)
    )


def logRequestSent(reqID: int) -> None:
    log(f"Sending request #{reqID}")


def logRequestReceivedSuccesfully(reqID: int) -> None:
    log(f"Request #{reqID} succeeded")


def log(logString: str) -> None:
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ; " + logString)
