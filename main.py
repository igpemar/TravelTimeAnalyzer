import time
import threading
import helpers.config as config
import helpers.logger as logger
import ETL.extract as extract
import ETL.pipeline as pipeline
import helpers.timemanagement as timemngmt
from PostProcessing.plotter import postProcess


REQ_SEND = 0
RESTART_INPUT = "Y"

if __name__ == "__main__":
    # Get configuration variables
    Config = config.Config(REQ_SEND)

    # Print intro message
    logger.logIntroMessage(Config.HOME, Config.WORK)

    # Checking for restart
    logger.log("Checking for restart...")
    TravelStats = extract.restartCheck(RESTART_INPUT)

    # Checking for start time
    timemngmt.waitForStartTime(Config)

    # Start ETL Pipeline
    t1 = threading.Thread(target=pipeline.ETLPipeline, args=(TravelStats, Config))
    t1.start()

    # Start PostProcessing service
    if Config.POST_PROCESSING:
        time.sleep(1)
        t2 = threading.Thread(
            target=postProcess,
            args=("Output.jpg", Config.POST_PROCESSING_SAMPLING_TIME),
        ).start()
