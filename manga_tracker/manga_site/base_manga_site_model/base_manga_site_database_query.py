import logging
from manga_tracker.database.manga_tracker_database import MangatrackerDatabase
from manga_tracker.database.database_creation_query import check_table_exists
connection = MangatrackerDatabase().instance.connection


class BaseMangaSiteDatabaseQueryDatabaseQuery:
    base_manga_site = None  # should be replaced by a string

    @classmethod
    def check_table_mangatracker_manga_id_to_base_manga_site_manga_id_exists(cls, cursor):
        table_name = "mangatracker_manga_id_to_{base_manga_site}_manga_id".format(base_manga_site=cls.base_manga_site)
        return check_table_exists(table_name, cursor)

    # TABLE CREATION QUERY
    @classmethod
    def create_table_mangatracker_manga_id_to_base_manga_site_manga_id_sql_query(cls):
        return """CREATE TABLE mangatracker_manga_id_to_{base_manga_site}_manga_id
                    (
                        mangatracker_manga_id MEDIUMINT UNSIGNED NOT NULL,
                        {base_manga_site}_manga_id VARCHAR(100) NOT NULL, -- 100 seems to be enough in size for now
                        PRIMARY KEY(mangatracker_manga_id),
                        FOREIGN KEY(mangatracker_manga_id) REFERENCES manga_id_to_english_title(manga_id),
                        UNIQUE ({base_manga_site}_manga_id)
                    );""".format(base_manga_site=cls.base_manga_site)

    @classmethod
    def create_table_mangatracker_manga_id_to_base_manga_site_manga_id(cls, cursor):
        if not cls.check_table_mangatracker_manga_id_to_base_manga_site_manga_id_exists(cursor):
            logging.info("Creating table for {}".format(cls.base_manga_site))
            cursor.execute(cls.create_table_mangatracker_manga_id_to_base_manga_site_manga_id_sql_query())
            logging.info("Table for {} created".format(cls.base_manga_site))

    # SELECT QUERY
    @classmethod
    def select_mangatracker_manga_id_from_base_manga_site_manga_id_sql_query(cls):
        return """SELECT mangatracker_manga_id
                  FROM mangatracker_manga_id_to_{base_manga_site}_manga_id
                  WHERE {base_manga_site}_manga_id LIKE %s""".format(base_manga_site=cls.base_manga_site)

    @classmethod
    def select_mangatracker_manga_id_from_base_manga_site_manga_id(cls, base_manga_site_manga_id, cursor):
        base_manga_site_manga_id = str(base_manga_site_manga_id)
        logging.info("Checking whether {base_manga_site} manga %s is in our database".format(
            base_manga_site=cls.base_manga_site) % base_manga_site_manga_id)
        sql_query = cls.select_mangatracker_manga_id_from_base_manga_site_manga_id_sql_query()
        cursor.execute(sql_query, base_manga_site_manga_id)
        mangatracker_manga_id = cursor.fetchone()
        if mangatracker_manga_id is None:
            logging.info("{base_manga_site} manga %s is not in our database".format(
                base_manga_site=cls.base_manga_site) % base_manga_site_manga_id)
        else:
            mangatracker_manga_id = mangatracker_manga_id['mangatracker_manga_id']
            logging.info("{base_manga_site} manga %s is in our database with manga id %d".format(
                base_manga_site=cls.base_manga_site)
                         % (base_manga_site_manga_id, mangatracker_manga_id))
        return mangatracker_manga_id

    check_if_chapter_already_in_database_sql_query = """SELECT 1
                                                        FROM chapter_id_to_resource_id
                                                        WHERE chapter_id = %s AND
                                                              website_id = %s AND
                                                              language_abbr = %s"""

    @staticmethod
    def check_if_chapter_already_in_database(chapter_id, website_id, language_abbr, cursor):
        query_tuple = str(chapter_id), str(website_id), str(language_abbr)
        logging.info("Checking if chapter %s website %s language %s is already in the database" % query_tuple)
        sql_query = BaseMangaSiteDatabaseQueryDatabaseQuery.check_if_chapter_already_in_database_sql_query
        cursor.execute(sql_query, query_tuple)
        result = cursor.fetchone()
        if result is not None:
            logging.info("Chapter %s website %s language %s is in the database" % query_tuple)
        else:
            logging.info("Chapter %s website %s language %s is not in the database" % query_tuple)
        return result is not None

    # INSERT QUERY
    @classmethod
    def insert_mangatracker_manga_id_to_base_manga_site_manga_id_sql_query(cls):
        return """INSERT INTO mangatracker_manga_id_to_{base_manga_site}_manga_id(mangatracker_manga_id, {base_manga_site}_manga_id)
                  VALUES (%s, %s)""".format(base_manga_site=cls.base_manga_site)

    @classmethod
    def insert_mangatracker_manga_id_to_base_manga_site_manga_id(cls, mangatracker_manga_id, base_manga_site_manga_id,
                                                                 cursor):
        query_tuple = str(mangatracker_manga_id), str(base_manga_site_manga_id)
        logging.info("Adding matching between mangatracker_manga_id %s and {base_manga_site}_manga_id %s".format(
            base_manga_site=cls.base_manga_site) % query_tuple)
        sql_query = cls.insert_mangatracker_manga_id_to_base_manga_site_manga_id_sql_query()
        cursor.execute(sql_query, query_tuple)
        connection.commit()
        logging.info("Matching between mangatracker_manga_id %s and {base_manga_site}s_manga_id %s was added".format(
            base_manga_site=cls.base_manga_site) % query_tuple)
