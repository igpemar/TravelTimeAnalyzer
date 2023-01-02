import threading
import ETL.extract as extract
import ETL.pipeline as pipeline
import helpers.config as config
import helpers.logger as logger
import helpers.timeutils as timemngmt

RESTART_INPUT = "Y"

if __name__ == "__main__":
    # Get configuration variables
    print("---------------------------------------------------------------------")
    logger.log("Parsing input parameteres...")
    Config = config.Config()

    # Print intro message
    logger.logIntroMessage(Config.A, Config.B)

    # Setting up database environment
    if Config.PERSIST_MODE.upper() == "DB":
        import db.connector as db

        try:
            db.setDatabases()
        except:
            logger.log("Unable to set databases, defaulting to csv dump mode.")
            Config.PERSIST_MODE = "csv"

    # Checking for restart
    logger.log("Checking for restart...")
    TravelStats = extract.restartCheck(Config, RESTART_INPUT)

    # Checking for start time
    timemngmt.waitForStartTime(Config)

    # Start ETL Pipeline
    t1 = threading.Thread(target=pipeline.ETLPipeline, args=(TravelStats, Config))
    t1.start()

    # Start PostProcessing service
    if Config.ENABLE_POST_PROCESSING:
        from PostProcessing.plotter import postProcess

        t2 = threading.Thread(
            target=postProcess,
            args=(Config, "Output.jpg"),
        ).start()
