import numpy as np


def storeRespDataNP(
    TravelTime,
    reqTimestamp,
    response,
):
    TravelTime.setTimeStamps(reqTimestamp)
    TravelTime.distanceAVG.append(
        round(response["rows"][0]["elements"][0]["distance"]["value"] / 1000.0, 2)
    )
    TravelTime.durationInclTraffic.append(
        round(
            response["rows"][0]["elements"][0]["duration_in_traffic"]["value"] / 60.0,
            2,
        )
    )
    TravelTime.durationEnclTraffic.append(
        round(response["rows"][0]["elements"][0]["duration"]["value"] / 60.0, 2)
    )


def travelTimeColumnStack(TravelTime):
    return np.column_stack(
        (
            TravelTime.reqID,
            TravelTime.timestampSTR,
            TravelTime.distanceAVG,
            TravelTime.durationEnclTraffic,
            TravelTime.durationInclTraffic,
        )
    )
