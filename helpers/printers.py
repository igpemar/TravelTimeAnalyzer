import helpers


def intro_message(config: helpers.config.Config):
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
