import logging
from manga_tracker.database.manga_tracker_database import MangatrackerDatabase


# INSERT QUERY
insert_followed_manga_sql_query = \
    """INSERT IGNORE INTO user_followed_manga(user_id, manga_id, next_volume_number_to_read, next_chapter_number_to_read)
       VALUES (%s, %s, %s, %s)"""


def insert_followed_manga(user_id, manga_id, volume_number, chapter_number, cursor):
    query_tuple = str(user_id), str(manga_id), str(volume_number), str(chapter_number)
    logging.info("User %s is adding manga_id %s vol %s chap %s to his followed manga" % query_tuple)
    cursor.execute(insert_followed_manga_sql_query, query_tuple)
    MangatrackerDatabase().connection.commit()
    logging.info("User %s added manga_id %s vol %s chap %s to his followed manga" % query_tuple)


insert_user_website_pref_sql_query = """INSERT INTO user_website_pref(user_id, website_id, pref_order)
                                        VALUES (%s, %s, %s)"""

insert_user_language_pref_sql_query = """INSERT INTO user_language_pref(user_id, language_abbr, pref_order)
                                         VALUES (%s, %s, %s)"""


def insert_user_pref(user_id, pref, pref_order, thing_to_order, cursor):
    user_id, thing_to_order, pref, pref_order = str(user_id), str(thing_to_order), str(pref), str(pref_order)
    logging.info("Inserting user %s %s pref" % (user_id, thing_to_order))

    if thing_to_order == "website":
        new_insert_user_pref_sql_query = insert_user_website_pref_sql_query
    else:
        new_insert_user_pref_sql_query = insert_user_language_pref_sql_query
    cursor.execute(new_insert_user_pref_sql_query, (user_id, pref, pref_order))
    MangatrackerDatabase().connection.commit()
    logging.info("User %s %s pref have been inserted" % (user_id, thing_to_order))


def insert_user_website_pref(user_id, pref, pref_order, cursor):
    insert_user_pref(user_id, pref, pref_order, "website", cursor)


def insert_user_language_pref(user_id, pref, pref_order, cursor):
    insert_user_pref(user_id, pref, pref_order, "language", cursor)


# DELETE QUERY
delete_user_pref_sql_query = """DELETE FROM user_{thing_to_order}_pref
                                WHERE user_id = %s"""


def delete_user_pref(user_id, thing_to_order, cursor):
    user_id, thing_to_order = str(user_id), str(thing_to_order)
    logging.info("Deleting user %s %s pref" % (user_id, thing_to_order))
    new_delete_user_pref_sql_query = delete_user_pref_sql_query.format(thing_to_order=thing_to_order)
    cursor.execute(new_delete_user_pref_sql_query, user_id)
    MangatrackerDatabase().connection.commit()
    logging.info("User %s %s pref have been deleted" % (user_id, thing_to_order))


def delete_user_website_pref(user_id, cursor):
    delete_user_pref(user_id, "website", cursor)


def delete_user_language_pref(user_id, cursor):
    delete_user_pref(user_id, "language", cursor)
