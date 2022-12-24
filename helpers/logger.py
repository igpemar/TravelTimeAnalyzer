import datetime
import helpers.config


def printIntroMessage(config: helpers.config.Config):
    homeCardinalLat = " N ; "
    workCardinalLat = " N ; "
    if config.HOME[0] < 0:
        homeCardinalLat = " S ; "
    if config.WORK[0] < 0:
        workCardinalLat = " S ; "

    homeCardinalLon = " E "
    workCardinalLon = " E "
    if config.HOME[0] < 0:
        homeCardinalLon = " W "
    if config.WORK[0] < 0:
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
    print(
        "   "
        + str(config.HOME[0])
        + homeCardinalLat
        + str(config.HOME[1])
        + homeCardinalLon
    )
    print(" to:")
    print(
        "   "
        + str(config.WORK[0])
        + workCardinalLat
        + str(config.WORK[1])
        + workCardinalLon
    )
    print(
        "------------------------------------------------------------------------------"
    )


def printWaitTimeMessage(start_time: str) -> None:
    log(
        "Current time: "
        + str(datetime.datetime.now())
        + "  ; Waiting for Startime ... "
        + str(start_time)
    )


def printRequestSent(reqID):
    log(f"Sending request #{reqID}")


def printRequestReceivedSuccesfully(reqID):
    log(f"Request #{reqID} succeeded")


def log(logString: str):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ; " + logString)
