import time
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import ETL.extract as extract
import helpers.datastructures as ds
import helpers.config as config
from datetime import datetime as datetime
from datetime import timedelta as timedelta

axis_mode = "FullDay"  # Choose between "Running", "FullWeek" and "FullDay"

Vector = list[float]


def postProcess(config: config.Config, SAVE_LOCATION: str = "Plot.jgp") -> None:
    sampling = config.POST_PROCESSING_INTERVAL
    if not checkAxisMode(axis_mode):
        raise Exception("wrong axis_mode")
    while True:
        # Reading the data
        TravelStats = extract.fetchData(config, "Output")
        if TravelStats.A2B.isFirstWriteCycle:
            continue

        matplotlib.use("agg")

        # Plotting
        (ax1, ax2) = createFigure()
        initializeAxes(
            ax1,
            XLABEL="Elapsed Time [s]",
            XLAB_FS=15,
            YLABEL="Commute Time (incl. traffic)  [min]",
            YLAB_FS=15,
        )
        initializeAxes(
            ax2,
            XLABEL="Elapsed Time [s]",
            XLAB_FS=15,
            YLABEL="Distance  [km]",
            YLAB_FS=15,
        )

        # Plotting duration including traffic vs elapsed time in seconds
        X, Y1, Y2 = parseDurationInclTraffic2XYPlot(TravelStats)
        if not checkForDataCompletion(config, X, Y1, Y2):
            continue
        ax1.plot(X, Y1, "b.")
        if config.RETURNMODE:
            ax1.plot(X, Y2, "r.")
        else:
            Y2 = [0]
        setYLim(ax1, Y1, Y2)

        # Plotting distance vs elapsed time in seconds
        X, Y1, Y2 = parseDistance2XYPlot(TravelStats)
        if not checkForDataCompletion(config, X, Y1, Y2):
            continue
        ax2.plot(X, Y1, "b.")
        if config.RETURNMODE:
            ax2.plot(X, Y2, "r.")
        else:
            Y2 = [0]
        setYLim(ax2, Y1, Y2)

        # Set xticks and labels
        XTicks = getXTicks(axis_mode)
        t0 = TravelStats.A2B.timestampDT[0]
        XTicksLabels = getXLabels(t0, axis_mode)
        if len(XTicks) > 0:
            ax1.set_xticks(XTicks, labels=XTicksLabels, rotation=45)
            ax2.set_xticks(XTicks, labels=XTicksLabels, rotation=45)

        ax1.grid()
        ax2.grid()

        plt.savefig(SAVE_LOCATION)

        if sampling > 0:
            time.sleep(sampling)
        else:
            break


def initializeAxes(
    ax: plt.axes,
    XLABEL: str = "X label",
    YLABEL: str = "Y label",
    XLAB_FS: int = 15,
    YLAB_FS: int = 15,
) -> None:
    ax.set_xlabel(XLABEL, fontsize=XLAB_FS)
    ax.set_ylabel(YLABEL, fontsize=YLAB_FS)


def setYLim(ax: plt.axes, Y1: Vector, Y2: Vector) -> None:
    ax.set_ylim((0, math.ceil(1.1 * max(max(Y1), max(Y2)))))


def buildOutputsSourcePaths(SourcePath: str, Filename: str) -> tuple[str, str]:
    if SourcePath:
        if SourcePath[-1] != "/":
            SourcePath += "/"

    return (
        SourcePath + Filename + "_" + "_A2B.csv",
        SourcePath + Filename + "_" + "_B2A.csv",
    )


def createFigure() -> tuple[plt.axes, plt.axes]:
    plt.close("all")
    _, (ax1, ax2) = plt.subplots(1, 2, num=1, figsize=(20, 10))
    return (ax1, ax2)


def parseDurationInclTraffic2XYPlot(
    TravelStats: ds.TravelStats,
) -> tuple[Vector, Vector, Vector]:
    timestamp = TravelStats.A2B.timestampDT
    t0 = timestamp[0]
    elapsedTimeSeconds = [(x - t0).total_seconds() for x in timestamp]
    Y1 = TravelStats.A2B.durationInclTraffic
    Y2 = TravelStats.B2A.durationInclTraffic
    return elapsedTimeSeconds, Y1, Y2


def parseDurationExclTraffic2XYPlot(
    TravelStats: ds.TravelStats,
) -> tuple[Vector, Vector, Vector]:
    timestamp = TravelStats.A2B.timestampDT
    t0 = timestamp[0]
    elapsedTimeSeconds = [(x - t0).total_seconds() for x in timestamp]
    Y1 = TravelStats.A2B.durationEnclTraffic
    Y2 = TravelStats.B2A.durationEnclTraffic
    return elapsedTimeSeconds, Y1, Y2


def parseDistance2XYPlot(
    TravelStats: ds.TravelStats,
) -> tuple[Vector, Vector, Vector]:
    timestamp = TravelStats.A2B.timestampDT
    t0 = timestamp[0]
    elapsedTimeSeconds = [(x - t0).total_seconds() for x in timestamp]
    Y1 = TravelStats.A2B.distanceAVG
    Y2 = TravelStats.B2A.distanceAVG
    return elapsedTimeSeconds, Y1, Y2


def getXTicks(axis_mode: str) -> np.ndarray:
    if axis_mode == "FullWeek":
        return np.linspace(0, 60 * 60 * 24 * 7, len(range(0, 7 * 24 + 8, 8)))
    elif axis_mode == "FullDay":
        return np.linspace(0, 60 * 60 * 24, len(range(0, 1 * 24 + 1, 1)))
    else:
        return []


def getXLabels(t0: datetime, axis_mode: str) -> list[str]:
    if axis_mode == "FullWeek":
        return [
            str((t0 + timedelta(hours=int(i), minutes=-t0.minute, seconds=-t0.second)))[
                :-3
            ]
            for i in range(0, 7 * 24 + 8, 8)
        ]
    elif axis_mode == "FullDay":
        return [
            str((t0 + timedelta(hours=int(i), minutes=-t0.minute, seconds=-t0.second)))[
                :-3
            ]
            for i in range(0, 1 * 24 + 1, 1)
        ]
    else:
        return []


def checkAxisMode(axis_mode: str) -> bool:
    if axis_mode == "Running":
        return True
    elif axis_mode == "FullDay":
        return True
    elif axis_mode == "FullWeek":
        return True
    else:
        return False


def checkForDataCompletion(config: config.Config, X: list, Y1: list, Y2: list) -> bool:
    if config.RETURNMODE:
        return len(X) == len(Y1) and len(X) == len(Y2)
    return len(X) == len(Y1)
