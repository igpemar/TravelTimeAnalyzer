import sys
import psycopg2
import helpers.logger as logger

createTableCommands = (
    """
        CREATE TABLE IF NOT EXISTS A2B (
            reqID INTEGER PRIMARY KEY,
            timestampSTR VARCHAR NOT NULL,
            distanceAVG FLOAT NOT NULL,
            durationInclTraffic FLOAT NOT NULL,
            durationExclTraffic FLOAT NOT NULL
        );
        """,
    """
        CREATE TABLE IF NOT EXISTS B2A (
            reqID INTEGER PRIMARY KEY,
            timestampSTR VARCHAR NOT NULL,
            distanceAVG FLOAT NOT NULL,
            durationInclTraffic FLOAT NOT NULL,
            durationExclTraffic FLOAT NOT NULL
        );
        """,
)


class dbConfig:
    def __init__(self):
        self.HOST = "localhost"
        self.DOCKER_DB_HOST = "travelAnalyzerDB"
        self.PORT = 5432
        self.NAME = "travelAnalyzer"
        self.USER = "postgres"
        self.PASS = "postgres"
        self.STARTUP_COMMANDS = createTableCommands


def getDBConfig():
    return dbConfig()


def connect2DB(dbConfig: dbConfig):
    try:
        conn = psycopg2.connect(
            dbname=dbConfig.NAME,
            user=dbConfig.USER,
            password=dbConfig.PASS,
            host=dbConfig.HOST,
            port=dbConfig.PORT,
        )
        logger.log("Database connection established")
        return conn
    except psycopg2.OperationalError as e:
        try:
            conn = psycopg2.connect(
                dbname=dbConfig.NAME,
                user=dbConfig.USER,
                password=dbConfig.PASS,
                host=dbConfig.DOCKER_DB_HOST,
                port=dbConfig.PORT,
            )
            logger.log("Database connection established")
            return conn
        except psycopg2.OperationalError as e:
            logger.log(
                f"Failed to connect to database {dbConfig.NAME} in port {dbConfig.PORT}: {e}"
            )
            sys.exit(0)


def createDBTables(conn: psycopg2.connect, dbConfig: dbConfig):
    cursor = conn.cursor()
    for command in dbConfig.STARTUP_COMMANDS:
        cursor.execute(command)
    try:
        conn.commit()
        logger.log(" Tables created succesfully")
        cursor.close()
    except Exception as e:
        logger.log(f" Failed to create tables in database: {e}")
        sys.exit()


def setDatabases():
    dbConfig = getDBConfig()
    conn = connect2DB(dbConfig)
    createDBTables(conn, dbConfig)
    closeDBconnection(conn)


def getAll(conn: psycopg2.connect, tableName: str):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM " + tableName.lower())
    conn.commit()

    rows = cursor.fetchall()
    cursor.close()
    return rows


def persistRow(conn: psycopg2.connect, tableName: str, row):
    cursor = conn.cursor()

    insertCommand = f"""
        INSERT INTO {tableName}
        VALUES({row[0]},'{row[1]}',{row[2]},{row[3]},{row[4]})
        ON CONFLICT DO NOTHING;
        """
    cursor.execute(insertCommand)
    conn.commit()


def flushdbs(conn: psycopg2.connect):
    cursor = conn.cursor()
    flushCommand = f"""
        DELETE FROM A2B
        where reqid is not null;
        """
    cursor.execute(flushCommand)
    flushCommand = f"""
        DELETE FROM B2A
        where reqid is not null;
        """
    cursor.execute(flushCommand)
    try:
        conn.commit()
        logger.log(" Database tables flushed successfully")
        cursor.close()
    except Exception as e:
        logger.log(f" Failed to flused tables in database tables: {e}")
        sys.exit()
    closeDBconnection(conn)


def closeDBconnection(conn: psycopg2.connect):
    conn.close()
    logger.log("Database connection closed")
