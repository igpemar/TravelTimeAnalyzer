import time
import datetime
import threading
import numpy as np
import PostProcessing.plotter
import helpers.config, helpers.logger
import ETL.extract, ETL.transform, ETL.load, ETL.pipeline


REQ_SEND = 0
RESTART_INPUT = "Y"


if __name__ == "__main__":
    # Get configuration variables
    config = helpers.config.Config(REQ_SEND)

    # Print intro message
    helpers.logger.printIntroMessage(config)

    # Checking for restart
    print("Checking for restart...")
    TravelStats = ETL.extract.restart_check(RESTART_INPUT)

    # Checking for start time
    while helpers.config.isItTimeToStart(config.START_TIME):
        helpers.logger.printWaitTimeMessage(config.START_TIME)
        time.sleep(5)

    print("Starting now at: ", datetime.datetime.now())

    # Start ETL Pipeline
    # ETL.pipeline.ETLPipeline(TravelStats, config)
    t1 = threading.Thread(target=ETL.pipeline.ETLPipeline, args=(TravelStats, config))
    t1.start()

    # Start PostProcessing service
    if config.POST_PROCESSING:
        t2 = threading.Thread(
            target=PostProcessing.plotter.postProcess,
            args=(False, True, "Output.jpg", config.POST_PROCESSING_SAMPLING_TIME),
        )
        t2.start()
