import numpy as np
import ETL.extract as extract


def storeRespDataNP(
    TravelTime,
    reqTimestamp,
    response,
):
    root = response["rows"][0]["elements"][0]
    TravelTime.setTimeStamps(reqTimestamp)
    TravelTime.distanceAVG.append(round(root["distance"]["value"] / 1000.0, 2))
    TravelTime.durationInclTraffic.append(
        round(
            root["duration_in_traffic"]["value"] / 60.0,
            2,
        )
    )
    TravelTime.durationEnclTraffic.append(round(root["duration"]["value"] / 60.0, 2))
    TravelTime.isFirstWriteCycle = False


def travelTimeColumnStack(TravelTime: extract.TravelTime) -> np.ndarray:
    return np.column_stack(
        (
            TravelTime.reqID,
            TravelTime.timestampSTR,
            TravelTime.distanceAVG,
            TravelTime.durationEnclTraffic,
            TravelTime.durationInclTraffic,
        )
    )
