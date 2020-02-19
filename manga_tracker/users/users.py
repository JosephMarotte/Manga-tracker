import logging
from manga_tracker.database.manga_tracker_database import MangatrackerDatabase
from manga_tracker.users import users_database_query
connection = MangatrackerDatabase().instance.connection


class Users:
    def __init__(self, user_id=None):
        if user_id is None:
            self.user_id = Users.add_user_to_database()
            self.rank_website_pref([1])
            self.rank_language_pref(["eng"])
        else:
            self.user_id = user_id

    @staticmethod
    def add_user_to_database():
        logging.info("Adding new user to the database")
        with connection.cursor() as cursor:
            sql = "INSERT INTO users VALUES ()"
            cursor.execute(sql)
            user_id = cursor.lastrowid
        connection.commit()
        logging.info("The new user id is %d")
        return user_id

    def add_new_followed_manga_id(self, manga_id):
        logging.info("Adding manga_id {} to the followed manga of user {}".format(manga_id, self.user_id))
        with connection.cursor() as cursor:
            users_database_query.insert_followed_manga(self.user_id, manga_id, "0.0", 0, cursor)

    def add_new_followed_manga_name(self, title):
        # retrieve manga_id for this manga
        title = title.lower()
        logging.info("Retrieving manga_id for manga {}".format(title))
        with connection.cursor() as cursor:
            sql = """SELECT manga_id
                     FROM manga_id_to_english_title
                     WHERE title = %s"""
            cursor.execute(sql, title)
            manga_id = cursor.fetchone()
            if manga_id is None:
                logging.info("Manga {} is not in our database".format(title))
            else:
                manga_id = int(manga_id['manga_id'])
                logging.info("Manga {} has id {}".format(title, manga_id))
                self.add_new_followed_manga_id(manga_id)

    def add_new_followed_manga_list(self, title_or_manga_id_list):
        for title_or_manga_id in title_or_manga_id_list:
            self.add_new_followed_manga(title_or_manga_id)

    def add_new_followed_manga(self, title_or_manga_id):
        title_or_manga_id = str(title_or_manga_id)
        if title_or_manga_id.isdigit():
            self.add_new_followed_manga_id(int(title_or_manga_id))
        else:
            self.add_new_followed_manga_name(title_or_manga_id)

    def change_followed_manga(self, manga_id, new_volume_number, new_chapter_number):
        logging.info("Changing last volume number and chapter number for manga_id %d of user %d" % (manga_id, self.user_id))
        with connection.cursor() as cursor:
            sql = "UPDATE user_followed_manga " \
                  "SET next_volume_number_to_read = %d, " \
                  "    next_chapter_number_to_read = %s " \
                  "WHERE user_id = %d" % (new_volume_number, new_chapter_number, self.user_id)
            cursor.execute(sql)
        connection.commit()
        logging.info("Last volume number was changed to %d and chapter number was changed to %s"
                     % (new_volume_number, new_chapter_number))

    # TODO maybe try to merge the code of rank_website_pref and rank_language_pref
    def rank_website_pref(self, website_id_ranking):
        with connection.cursor() as cursor:
            users_database_query.delete_user_website_pref(self.user_id, cursor)
            for (rank, website_id) in enumerate(website_id_ranking):
                users_database_query.insert_user_website_pref(self.user_id, website_id, rank, cursor)

    def rank_language_pref(self, language_abbr_ranking):
        with connection.cursor() as cursor:
            users_database_query.delete_user_language_pref(self.user_id, cursor)
            for (rank, language_abbr) in enumerate(language_abbr_ranking):
                users_database_query.insert_user_language_pref(self.user_id, language_abbr, rank, cursor)

    def retrieve_followed_manga(self):
        # TODO try to make this query shorter
        sql = \
            """
            SELECT mici.chapter_id,
                   ANY_VALUE(ufm.manga_id) as manga_id, 
                   ANY_VALUE(miet.title) as title,
                   ANY_VALUE(mici.volume_number) as volume_number,
                   ANY_VALUE(mici.chapter_number) as chapter_number,
                   ANY_VALUE(ciri.resource_id) as resource_id,
                   ANY_VALUE(ciri.website_id) as website_id,
                   ANY_VALUE(ciri.language_abbr) as language_abbr
            FROM users u, user_followed_manga ufm, user_language_pref ulp, user_website_pref uwp, manga_id_to_chapter_id mici,
                 chapter_id_to_resource_id ciri, manga_id_to_english_title miet
                 JOIN (
                     SELECT mici.chapter_id, MIN(ulp.pref_order) as score
                     FROM users u, user_followed_manga ufm, user_language_pref ulp, user_website_pref uwp, manga_id_to_chapter_id mici,
                          chapter_id_to_resource_id ciri
                          JOIN (
                                 SELECT mici.chapter_id, MIN(uwp.pref_order) as score
                                 FROM users u, user_followed_manga ufm, user_language_pref ulp, user_website_pref uwp, manga_id_to_chapter_id mici,
                                      chapter_id_to_resource_id ciri
                                 WHERE u.user_id = {user_id} AND
                                      ufm.user_id = u.user_id AND
                                      ulp.user_id = u.user_id AND
                                      uwp.user_id = u.user_id AND
                                      ufm.manga_id = mici.manga_id AND
                                      mici.chapter_id = ciri.chapter_id AND
                                      ciri.language_abbr = ulp.language_abbr AND
                                      ciri.website_id = uwp.website_id
                                 GROUP BY mici.chapter_id
                               ) best_score
                     WHERE u.user_id = {user_id} AND
                          ufm.user_id = u.user_id AND
                          ulp.user_id = u.user_id AND
                          uwp.user_id = u.user_id AND
                          ufm.manga_id = mici.manga_id AND
                          mici.chapter_id = ciri.chapter_id AND
                          ciri.language_abbr = ulp.language_abbr AND
                          ciri.website_id = uwp.website_id AND
                          best_score.score = uwp.pref_order AND
                          best_score.chapter_id = ciri.chapter_id
                     GROUP BY mici.chapter_id
                     ) best_score
            WHERE u.user_id = {user_id} AND
                  ufm.user_id = u.user_id AND
                  ulp.user_id = u.user_id AND
                  uwp.user_id = u.user_id AND
                  ufm.manga_id = mici.manga_id AND
                  (ufm.next_volume_number_to_read < mici.volume_number 
                   OR
                   ufm.next_volume_number_to_read = mici.volume_number AND ufm.next_chapter_number_to_read <= mici.chapter_number) AND
                  mici.chapter_id = ciri.chapter_id AND
                  ciri.language_abbr = ulp.language_abbr AND
                  ciri.website_id = uwp.website_id AND
                  best_score.chapter_id = ciri.chapter_id AND
                  best_score.score = ulp.pref_order AND
                  miet.manga_id = mici.manga_id
            GROUP BY mici.chapter_id
            """.format(user_id=self.user_id)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
