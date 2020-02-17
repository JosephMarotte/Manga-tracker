import logging
from manga_tracker.database.manga_tracker_database import MangatrackerDatabase

connection = MangatrackerDatabase().instance.connection

# SELECT QUERY
select_mangatracker_manga_id_from_leviathanscans_manga_id_sql_query = \
    """SELECT mangatracker_manga_id
       FROM mangatracker_manga_id_to_leviathanscans_manga_id
       WHERE leviathanscans_manga_id LIKE %s"""


def select_mangatracker_manga_id_from_leviathanscans_manga_id(leviathanscans_manga_id, cursor):
    leviathanscans_manga_id = str(leviathanscans_manga_id)
    logging.info("Checking whether leviathanscans manga %s is in our database" % leviathanscans_manga_id)
    cursor.execute(select_mangatracker_manga_id_from_leviathanscans_manga_id_sql_query, leviathanscans_manga_id)
    mangatracker_manga_id = cursor.fetchone()
    if mangatracker_manga_id is None:
        logging.info("Leviathanscans manga %s is not in our database" % leviathanscans_manga_id)
    else:
        mangatracker_manga_id = mangatracker_manga_id['mangatracker_manga_id']
        logging.info("Leviathanscans manga %s is in our database with manga id %d"
                     % (leviathanscans_manga_id, mangatracker_manga_id))
    return mangatracker_manga_id


check_if_chapter_already_in_database_sql_query = """SELECT 1
                                                    FROM chapter_id_to_resource_id
                                                    WHERE chapter_id = %s AND
                                                          website_id = %s AND
                                                          language_abbr = %s"""


def check_if_chapter_already_in_database(chapter_id, website_id, language_abbr, cursor):
    query_tuple = str(chapter_id), str(website_id), str(language_abbr)
    logging.info("Checking if chapter %s website %s language %s is already in the database" % query_tuple)
    cursor.execute(check_if_chapter_already_in_database_sql_query, query_tuple)
    result = cursor.fetchone()
    if result is not None:
        logging.info("Chapter %s website %s language %s is in the database" % query_tuple)
    else:
        logging.info("Chapter %s website %s language %s is not in the database" % query_tuple)
    return result is not None


# INSERT QUERY
insert_mangatracker_manga_id_to_leviathanscans_manga_id_sql_query = \
    """INSERT INTO mangatracker_manga_id_to_leviathanscans_manga_id(mangatracker_manga_id, leviathanscans_manga_id)
       VALUES (%s, %s)"""


def insert_mangatracker_manga_id_to_leviathanscans_manga_id(mangatracker_manga_id, leviathanscans_manga_id, cursor):
    query_tuple = str(mangatracker_manga_id), str(leviathanscans_manga_id)
    logging.info("Adding matching between mangatracker_manga_id %s and leviathanscans_manga_id %s" % query_tuple)
    cursor.execute(insert_mangatracker_manga_id_to_leviathanscans_manga_id_sql_query, query_tuple)
    connection.commit()
    logging.info("Matching between mangatracker_manga_id %s and leviathanscans_manga_id %s was added" % query_tuple)
