import logging


check_database_exists_sql_query = """SHOW DATABASES LIKE %s"""


def check_database_exist(database_name, cursor):
    database_name = str(database_name)
    logging.info("Check database {} exists".format(database_name))
    database_exists = cursor.execute(check_database_exists_sql_query, database_name) == 1
    if database_exists:
        logging.info("Database {} exists".format(database_name))
    else:
        logging.info("Database {} does not exists".format(database_name))
    return database_exists


create_database_sql_query = """CREATE DATABASE %s"""


def create_database(database_name, cursor):
    logging.info("Creating database {}".format(database_name))
    print(create_database_sql_query % database_name)
    cursor.execute(create_database_sql_query % database_name)
    logging.info("Database {} created".format(database_name))


def create_initial_tables(cursor):
    with open("database_creation.sql", "r") as f:
        queries = f.read()
    for query in queries.split(";")[:-1]:
        print(query)
        cursor.execute(query)


check_table_exists_sql_query = """SHOW TABLES LIKE %s"""


def check_table_exists(table_name, cursor):
    table_name = str(table_name)
    logging.info("Check table {} exists".format(table_name))
    table_exists = cursor.execute(check_table_exists_sql_query, table_name) == 1
    if table_exists:
        logging.info("Table {} exists".format(table_name))
    else:
        logging.info("Table {} does not exists".format(table_name))
    return table_exists
