import logging
from manga_tracker.database.manga_tracker_database import MangatrackerDatabase

connection = MangatrackerDatabase().instance.connection

# SELECT QUERY
select_mangadex_chapter_id_from_resource_id_sql_query = """SELECT mangadex_chapter_id
                                                           FROM resource_id_to_mangadex_chapter_id
                                                           WHERE resource_id = %s"""


def select_mangadex_chapter_id_from_resource_id(resource_id, cursor):
    resource_id = str(resource_id)
    logging.info("Retrieving chapter information for resource %s of mangadex." % resource_id)
    cursor.execute(select_mangadex_chapter_id_from_resource_id_sql_query, resource_id)
    return cursor.fetchone()["mangadex_chapter_id"]


select_mangatracker_manga_id_from_mangadex_manga_id_sql_query = """SELECT manga_id_mangatracker
                                                                   FROM manga_id_mangadex_to_manga_id_mangatracker
                                                                   WHERE manga_id_mangadex = %s"""


def check_if_mangadex_manga_id_is_in_database(mangadex_manga_id, cursor):
    mangadex_manga_id = str(mangadex_manga_id)
    logging.info("Check if manga %s of mangadex already in database" % mangadex_manga_id)
    cursor.execute(select_mangatracker_manga_id_from_mangadex_manga_id_sql_query, mangadex_manga_id)
    result = cursor.fetchone()
    if result is None:
        logging.info("Manga %s of mangadex is not in database" % mangadex_manga_id)
    else:
        logging.info("Manga %s of mangadex is in database" % mangadex_manga_id)
    return result is not None


def select_mangatracker_manga_id_from_mangadex_manga_id(mangadex_manga_id, cursor):
    mangadex_manga_id = str(mangadex_manga_id)
    logging.info("Retrieve mangatracker_manga_id for manga %s of mangadex." % mangadex_manga_id)
    cursor.execute(select_mangatracker_manga_id_from_mangadex_manga_id_sql_query, mangadex_manga_id)
    return cursor.fetchone()["manga_id_mangatracker"]


check_if_mangadex_chapter_id_is_in_database_sql_query = """SELECT 1
                                                           FROM resource_id_to_mangadex_chapter_id WHERE
                                                           mangadex_chapter_id = %s"""


def check_if_mangadex_chapter_id_is_in_database(chapter_id, cursor):
    chapter_id = str(chapter_id)
    logging.info("Check whether the mangadex chapter %s is already in our database" % chapter_id)
    cursor.execute(check_if_mangadex_chapter_id_is_in_database_sql_query, chapter_id)
    result = cursor.fetchone()
    if result is None:
        logging.info("Chapter %s of mangadex is not in our database" % chapter_id)
    else:
        logging.info("Chapter %s of mangadex is in our database" % chapter_id)
    return result is not None


get_max_mangadex_manga_id_sql_query = """SELECT max(manga_id_mangadex) as max_mangadex_manga_id
                                         FROM manga_id_mangadex_to_manga_id_mangatracker"""


def get_max_mangadex_manga_id(cursor):
    logging.info("Get maximum mangadex_manga_id")
    cursor.execute(get_max_mangadex_manga_id_sql_query)
    max_id = cursor.fetchone()["max_mangadex_manga_id"]
    max_id = 0 if max_id is None else max_id
    logging.info("Maximum mangadex_manga_id is %d" % max_id)
    return max_id


get_max_mangadex_chapter_id_sql_query = """SELECT max(mangadex_chapter_id) as max_mangadex_chapter_id
                                           FROM resource_id_to_mangadex_chapter_id"""


def get_max_mangadex_chapter_id(cursor):
    logging.info("Get maximum mangadex_chapter_id")
    cursor.execute(get_max_mangadex_chapter_id_sql_query)
    max_id = cursor.fetchone()["max_mangadex_chapter_id"]
    max_id = 0 if max_id is None else max_id
    logging.info("Maximum mangadex_chapter_id is %d" % max_id)
    return max_id


# INSERT QUERY
insert_mangatracker_manga_id_to_mangadex_manga_id_sql_query = \
    """INSERT INTO manga_id_mangadex_to_manga_id_mangatracker (manga_id_mangatracker, manga_id_mangadex)
       VALUES (%s, %s)"""


def insert_mangatracker_manga_id_to_mangadex_manga_id(mangatracker_manga_id, mangadex_manga_id, cursor):
    query_tuple = str(mangatracker_manga_id), str(mangadex_manga_id)
    logging.info("Adding matching between mangatracker_manga_id %s and mangadex_manga_id %s" % query_tuple)
    cursor.execute(insert_mangatracker_manga_id_to_mangadex_manga_id_sql_query, query_tuple)
    connection.commit()
    logging.info("Matching between mangatracker_manga_id %s and mangadex_manga_id %s added" % query_tuple)


insert_mangatracker_resource_id_to_mangadex_chapter_id_sql_query = \
    """INSERT INTO resource_id_to_mangadex_chapter_id(resource_id, mangadex_chapter_id)
       VALUES (%s, %s)"""


def insert_mangatracker_resource_id_to_mangadex_chapter_id(resource_id, mangadex_chapter_id, cursor):
    query_tuple = str(resource_id), str(mangadex_chapter_id)
    logging.info("Add binding between the resource id %s and the mangadex chapter id %s" % query_tuple)
    cursor.execute(insert_mangatracker_resource_id_to_mangadex_chapter_id_sql_query, query_tuple)
    connection.commit()
    logging.info("Binding between the resource id %s and the mangadex chapter id %s was added" % query_tuple)
