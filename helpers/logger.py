from datetime import datetime as datetime


def logIntroMessage(A: tuple, B: tuple) -> None:
    ACardinalLat = " N ; "
    ACardinalLat = " N ; "
    if A[0] < 0:
        ACardinalLat = " S ; "
    if B[0] < 0:
        ACardinalLat = " S ; "

    ACardinalLon = " E "
    ACardinalLon = " E "
    if A[0] < 0:
        ACardinalLon = " W "
    if B[0] < 0:
        ACardinalLon = " W "

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
    print("   " + str(A[0]) + ACardinalLat + str(A[1]) + ACardinalLon)
    print(" to:")
    print("   " + str(B[0]) + ACardinalLat + str(B[1]) + ACardinalLon)
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
