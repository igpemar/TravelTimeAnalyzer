import threading
import ETL.extract as extract
import ETL.pipeline as pipeline
import helpers.config as config
import helpers.logger as logger
import helpers.timeutils as timemngmt
import db.connector as db

REQ_SEND = 0
RESTART_INPUT = "N"
PERSIST_MODE = "db"  # choose between CSV and DB

if __name__ == "__main__":
    # Get configuration variables
    Config = config.Config(REQ_SEND)

    # Print intro message
    logger.logIntroMessage(Config.HOME, Config.WORK)

    # Setting up database environment
    if PERSIST_MODE.upper() == "DB":
        db.setDatabases()

    # Checking for restart
    logger.log("Checking for restart...")
    TravelStats = extract.restartCheck(RESTART_INPUT, PERSIST_MODE)

    # Checking for start time
    timemngmt.waitForStartTime(Config)

    # Start ETL Pipeline
    t1 = threading.Thread(target=pipeline.ETLPipeline, args=(TravelStats, Config))
    t1.start()

    # Start PostProcessing service
    if Config.POST_PROCESSING:
        from PostProcessing.plotter import postProcess

        t2 = threading.Thread(
            target=postProcess,
            args=("Output.jpg", Config.POST_PROCESSING_INTERVAL),
        ).start()
