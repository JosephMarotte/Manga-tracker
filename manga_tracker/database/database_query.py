import logging
from manga_tracker.database.manga_tracker_database import MangatrackerDatabase


# SELECT QUERY
select_manga_id_of_title_sql_query = """SELECT manga_id
                              FROM manga_id_to_english_title
                              WHERE title LIKE %s"""


def select_manga_id_of_title(title, cursor):
    title = str(title)
    logging.info("Checking if title %s is in our database", title)
    cursor.execute(select_manga_id_of_title_sql_query, title)
    mangatracker_manga_id = cursor.fetchone()
    if mangatracker_manga_id is None:
        logging.info("Title %s is not in our database", title)
    else:
        mangatracker_manga_id = mangatracker_manga_id["manga_id"]
        logging.info("Title %s is in our database with manga_id %d" % (title, mangatracker_manga_id))
        return mangatracker_manga_id
    return mangatracker_manga_id


select_chapter_id_from_manga_volume_chapter_sql_query = """SELECT mcid.chapter_id
                                                 FROM manga_id_to_chapter_id mcid
                                                 WHERE mcid.manga_id = %s AND
                                                       mcid.volume_number  = %s AND
                                                       mcid.chapter_number = %s"""


def select_chapter_id_from_manga_volume_chapter(manga_id, volume, chapter, cursor):
    manga_id, volume, chapter = str(manga_id), str(volume), str(chapter)
    query_tuple = manga_id, volume, chapter
    logging.info("Check if there is a mangatracker_chapter_id for manga %s volume %s chapter %s" % query_tuple)
    cursor.execute(select_chapter_id_from_manga_volume_chapter_sql_query, query_tuple)
    mangatracker_chapter_id = cursor.fetchone()
    if mangatracker_chapter_id is None:
        logging.info("There is no mangatracker_chapter_id for manga %s volume %s chapter %s" % query_tuple)
    else:
        mangatracker_chapter_id = mangatracker_chapter_id["chapter_id"]
        logging.info("Mangatracker_chapter_id %d for manga %s volume %s chapter %s"
                     % (mangatracker_chapter_id, manga_id, volume, chapter))
    return mangatracker_chapter_id


# INSERT QUERY
insert_title_sql_query = "INSERT INTO manga_id_to_english_title(title) VALUES (%s)"


def insert_title(title, cursor):
    title = str(title)
    logging.info("Adding title %s to the database" % title)
    cursor.execute(insert_title_sql_query, title)
    mangatracker_manga_id = cursor.lastrowid
    MangatrackerDatabase().connection.commit()
    logging.info("The title %s has been added to the database with id %d" % (title, mangatracker_manga_id))
    return mangatracker_manga_id


insert_manga_id_to_chapter_id_sql_query = """INSERT INTO manga_id_to_chapter_id(manga_id, volume_number, chapter_number) 
                                             VALUES (%s, %s, %s)"""


def insert_manga_id_to_chapter_id(manga_id, volume, chapter, cursor):
    manga_id, volume, chapter = str(manga_id), str(volume), str(chapter)
    logging.info("Adding manga %s volume %s chapter %s to the database")
    cursor.execute(insert_manga_id_to_chapter_id_sql_query, (manga_id, volume, chapter))
    MangatrackerDatabase().connection.commit()
    chapter_id = cursor.lastrowid
    logging.info("Manga %s volume %s chapter %s was added with chapter id %d" % (manga_id, volume, chapter, chapter_id))
    return chapter_id


insert_chapter_id_to_resource_id_sql_query = \
    """INSERT INTO chapter_id_to_resource_id(chapter_id, website_id, language_abbr)
       VALUES (%s, %s, %s)"""


def insert_chapter_id_to_resource_id(chapter_id, website_id, language_abbr, cursor):
    chapter_id, website_id, language_abbr = str(chapter_id), str(website_id), str(language_abbr)
    logging.info("Adding resource for chapter %s website %s language_abbr %s" % (chapter_id, website_id, language_abbr))
    cursor.execute(insert_chapter_id_to_resource_id_sql_query, (chapter_id, website_id, language_abbr))
    resource_id = cursor.lastrowid
    MangatrackerDatabase().connection.commit()
    logging.info("Chapter %s website %s language_abbr %s was added with resource_id %d"
                 % (chapter_id, website_id, language_abbr, resource_id))
    return resource_id
