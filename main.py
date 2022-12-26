import threading
import db.connector as db
import ETL.extract as extract
import ETL.pipeline as pipeline
import helpers.config as config
import helpers.logger as logger
import helpers.timeutils as timemngmt

RESTART_INPUT = "Y"

if __name__ == "__main__":
    # Get configuration variables
    Config = config.Config()

    # Print intro message
    logger.logIntroMessage(Config.A, Config.B)

    # Setting up database environment
    if config.PERSIST_MODE.upper() == "DB":
        db.setDatabases()

    # Checking for restart
    logger.log("Checking for restart...")
    TravelStats = extract.restartCheck(RESTART_INPUT, config.PERSIST_MODE)

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
            args=(Config, "Output.jpg"),
        ).start()
