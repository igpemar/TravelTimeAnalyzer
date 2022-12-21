import time
import datetime
import threading
import numpy as np
import PostProcessing.plotter
import helpers.config as config
import helpers.logger as logger
import ETL.extract, ETL.transform, ETL.load, ETL.pipeline


REQ_SEND = 0
RESTART_INPUT = "Y"

if __name__ == "__main__":
    # Get configuration variables
    Config = config.Config(REQ_SEND)

    # Print intro message
    logger.printIntroMessage(Config)

    # Checking for restart
    logger.log("Checking for restart...")
    TravelStats = ETL.extract.restartCheck(RESTART_INPUT)

    # Checking for start time
    config.waitForStartTime(Config)

    # Start ETL Pipeline
    t1 = threading.Thread(target=ETL.pipeline.ETLPipeline, args=(TravelStats, Config))
    t1.start()

    # Start PostProcessing service
    if Config.POST_PROCESSING:
        time.sleep(1)
        t2 = threading.Thread(
            target=PostProcessing.plotter.postProcess,
            args=("Output.jpg", Config.POST_PROCESSING_SAMPLING_TIME),
        ).start()
