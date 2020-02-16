import logging
import pymysql.cursors
from src.users.create_feed_from_manga_list import create_feed
from pprint import pprint

# TODO not have password / users hardcoded. And handle connection in a better way
connection = pymysql.connect(host='localhost',
                             user='joseph',
                             password='dosaku',
                             db='manga_tracker',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


class Users:
    def __init__(self, user_id = None):
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
        logging.info("The new user id is %d" )
        return user_id

    def add_new_followed_manga_list(self, manga_id_list):
        for manga_id in manga_id_list:
            self.add_new_followed_manga(manga_id)

    def add_new_followed_manga(self, manga_id):
        logging.info("Adding manga_id %d to the followed manga of user %d" % (manga_id, self.user_id))
        with connection.cursor() as cursor:
            sql = "INSERT IGNORE INTO user_followed_manga(user_id, manga_id, next_volume_number_to_read, next_chapter_number_to_read)" \
                  "VALUES (%d, %d, 0, 0)" % (self.user_id, manga_id)
            cursor.execute(sql)
        connection.commit()
        logging.info("Manga_id %d was added to the followed manga of user %d" % (manga_id, self.user_id))

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
        # TODO this can probably be improved
        # 1) delete previous website ranking
        with connection.cursor() as cursor:
            sql = "DELETE FROM user_website_pref WHERE user_id = %d" % self.user_id
            cursor.execute(sql)
        connection.commit()
        # 2) Add new website ranking
        with connection.cursor() as cursor:
            for (rank, website_id) in enumerate(website_id_ranking):
                sql = "INSERT INTO user_website_pref(user_id, website_id, pref_order) VALUES (%d, %d, %d)"\
                      % (self.user_id, website_id, rank)
                cursor.execute(sql)
        connection.commit()

    def rank_language_pref(self, language_abbr_ranking):
        # TODO this can probably be improved
        # 1) delete previous abbr ranking
        with connection.cursor() as cursor:
            sql = "DELETE FROM user_language_pref WHERE user_id = %d" % self.user_id
            cursor.execute(sql)
        connection.commit()
        # 2) Add new abbr ranking
        with connection.cursor() as cursor:
            for (rank, language_abbr) in enumerate(language_abbr_ranking):
                sql = "INSERT INTO user_language_pref(user_id, language_abbr, pref_order) VALUES (%d, '%s', %d)"\
                      % (self.user_id, language_abbr, rank)
                cursor.execute(sql)
        connection.commit()


def retrieve_followed_manga(user_id):
    # TODO try to make this query shorter
    sql = \
        """
        SELECT mici.chapter_id,
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
                             WHERE u.user_id = %d AND
                                  ufm.user_id = u.user_id AND
                                  ulp.user_id = u.user_id AND
                                  uwp.user_id = u.user_id AND
                                  ufm.manga_id = mici.manga_id AND
                                  mici.chapter_id = ciri.chapter_id AND
                                  ciri.language_abbr = ulp.language_abbr AND
                                  ciri.website_id = uwp.website_id
                             GROUP BY mici.chapter_id
                           ) best_score
                 WHERE u.user_id = %d AND
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
        WHERE u.user_id = %d AND
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
        """ % (user_id, user_id, user_id)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
