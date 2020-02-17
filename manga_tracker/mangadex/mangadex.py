import pymysql.cursors
import requests
import json
import logging
from manga_tracker.mangadex.mangadex_utils import mangadex_abbr_to_mangatracker_abbr

# TODO not have password / users hardcoded. And handle connection in a better way
connection = pymysql.connect(host='localhost',
                             user='joseph',
                             password='dosaku',
                             db='manga_tracker',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


MANGADEX = "mangadex"


class Mangadex:
    # TODO take into account this siteRateLimit
    siteRateLimit = 600  # 600 in 600s
    # TODO automatically generate website id first time class is seen
    website_id_mangadex = 1

    @staticmethod
    def get_full_title_url(mangadex_title_id):
        return "https://mangadex.org/manga/%d" % mangadex_title_id

    @staticmethod
    def get_full_chapter_url(mangadex_chapter_id):
        return "https://mangadex.org/chapter/%d" % mangadex_chapter_id

    @staticmethod
    def get_full_title_api_url(mangadex_title_id):
        return "https://mangadex.org/api/manga/%d" % mangadex_title_id

    @staticmethod
    def get_full_chapter_api_url(mangadex_chapter_id):
        return "https://mangadex.org/api/chapter/%d" % mangadex_chapter_id

    @staticmethod
    def retrieve_chapter_url(chapter):
        """chapter = {'chapter_id': 374,
                      'chapter_number': Decimal('12.0'),
                      'language_abbr': 'eng',
                      'resource_id': 1188,
                      'volume_number': 2,
                      'website_id': 1}"""
        with connection.cursor() as cursor:
            logging.info("Retrieving chapter information for resource %d of mangadex." % chapter["resource_id"])
            sql = """SELECT mangadex_chapter_id
                     FROM resource_id_to_mangadex_chapter_id
                     WHERE resource_id = %d""" % chapter["resource_id"]
            cursor.execute(sql)
            result = cursor.fetchone()
            mangadex_chapter_id = result["mangadex_chapter_id"]
            return Mangadex.get_full_chapter_url(mangadex_chapter_id)

    @staticmethod
    def get_title_data(mangadex_manga_id):
        # TODO add error case with the code
        r = requests.get(Mangadex.get_full_title_api_url(mangadex_manga_id), auth=('users', 'pass'))

        manga_data = json.loads(r.text)
        title = manga_data['manga']['title']

        # check whether the mangadex title exists or not
        with connection.cursor() as cursor:
            logging.info("Check if manga %d of mangadex already in database" % mangadex_manga_id)
            sql = "SELECT 1 " \
                  "FROM manga_id_mangadex_to_manga_id_mangatracker m " \
                  "WHERE m.manga_id_mangadex = %d" % mangadex_manga_id
            cursor.execute(sql)
            result = cursor.fetchone()
            if result is None:
                logging.info("Manga %d of mangadex not in database" % mangadex_manga_id)
                logging.info("Check if there is a manga id in database for this manga title %s" % title)
                sql = "Select manga_id " \
                      "FROM manga_id_to_english_title " \
                      "WHERE title LIKE '%s'" % title
                cursor.execute(sql)
                mangatracker_manga_id = cursor.fetchone()
                if mangatracker_manga_id is None:
                    logging.info("There was no manga in database for the manga title %s" % title)
                    logging.info("Adding new manga id to database for manga title %s" % title)
                    sql = "INSERT INTO manga_id_to_english_title(title) VALUES (%s)"
                    cursor.execute(sql, title)
                    mangatracker_manga_id = cursor.lastrowid
                else:
                    mangatracker_manga_id = mangatracker_manga_id['manga_id']
                    logging.info("Mangatracker id %d match this manga title %s" % (mangatracker_manga_id, title))
                logging.info("Adding matching between mangatracker_manga_id %d and mangadex_manga_id %d"
                             % (mangatracker_manga_id, mangadex_manga_id))
                sql = "INSERT INTO manga_id_mangadex_to_manga_id_mangatracker (manga_id_mangatracker, manga_id_mangadex) \
                       VALUES (%s, %s)"
                cursor.execute(sql, (mangatracker_manga_id, mangadex_manga_id))
            else:
                logging.info("Manga %d of mangadex was already in database" % mangadex_manga_id)

        connection.commit()

        for str_mangadex_chapter_id in manga_data['chapter']:
            chapter_data = manga_data['chapter'][str_mangadex_chapter_id]
            chapter_data['manga_id'] = mangadex_manga_id
            mangadex_chapter_id = int(str_mangadex_chapter_id) # int(str_mangadex_chapter_id)  # from str to int
            Mangadex.get_chapter_data_to_database(mangadex_chapter_id, True, chapter_data)

    @staticmethod
    def get_chapter_data_to_database(mangadex_chapter_id, check_if_already_in_database=True, chapter_data=None):
        """ Retrieving chapter data when we read manga data with the API """
        if check_if_already_in_database:
            logging.info("Check whether the mangadex chapter %d is already in our database" % mangadex_chapter_id)
            with connection.cursor() as cursor:
                sql = "SELECT 1 FROM resource_id_to_mangadex_chapter_id WHERE mangadex_chapter_id = %d" % mangadex_chapter_id
                cursor.execute(sql)
                resource_id = cursor.fetchone()
                if resource_id is not None:
                    logging.info("The mangadex chapter %d is already in our database" % mangadex_chapter_id)
                    return

        if chapter_data is None:
            logging.info("Retrieving chapter data of chapter %d" % mangadex_chapter_id)
            r = requests.get(Mangadex.get_full_chapter_api_url(mangadex_chapter_id), auth=('users', 'pass'))
            chapter_data = json.loads(r.text)
            logging.info("Chapter data of chapter %d were retrieved" % mangadex_chapter_id)

        # In some case volume and chapter are empty (for example for Oneshots). Artificially build it.
        if chapter_data['volume'] == "":
            chapter_data['volume'] = '1'
        if chapter_data['chapter'] == "":
            chapter_data['chapter'] = '1'

        mangadex_manga_id = chapter_data['manga_id']
        with connection.cursor() as cursor:
            logging.info("Checking whether a mangatracker_chapter_id exists for this chapter")

            # Retrieve the mangatracker_manga_id
            # TODO in some case we already computed manga_id_mangatracker from reading the manga, we may not recompute
            # TODO here but only pass it as an argument to the function
            logging.info("Retrieve mangatracker_manga_id for mangadex_manga_id")
            sql = "SELECT m.manga_id_mangatracker " \
                  "FROM manga_id_mangadex_to_manga_id_mangatracker m " \
                  "WHERE m.manga_id_mangadex = %d" % mangadex_manga_id
            cursor.execute(sql)
            mangatracker_manga_id = cursor.fetchone()['manga_id_mangatracker']

            # Retrieve mangatracker_chapter_id for this chapter
            # TODO probably possible to do something smarter using INSERT IGNORE
            logging.info("Retrieve possible mangatracker_chapter_id for this manga vol and chapter")
            sql = "SELECT mcid.chapter_id " \
                  "FROM manga_id_to_chapter_id mcid " \
                  "WHERE mcid.volume_number  = %d AND " \
                  "      mcid.chapter_number = %s AND " \
                  "      mcid.manga_id       = %d" % (int(chapter_data['volume']), chapter_data['chapter'], mangatracker_manga_id)
            cursor.execute(sql)
            mangatracker_chapter_id = cursor.fetchone()

            if mangatracker_chapter_id is None:
                logging.info("Add new chapter_id to mangatracker database")
                sql = "INSERT INTO manga_id_to_chapter_id(manga_id, volume_number, chapter_number) VALUES (%d, %d, %s)" \
                      % (mangatracker_manga_id, int(chapter_data['volume']), chapter_data['chapter'])
                cursor.execute(sql)
                mangatracker_chapter_id = cursor.lastrowid
                logging.info("chapter_id %d added to the mangatracker database" % mangatracker_chapter_id)
                connection.commit()
            else:
                mangatracker_chapter_id = mangatracker_chapter_id['chapter_id']
            logging.info("Add binding between this chapter_id %d and a new ressource_id")

            language_abbr = mangadex_abbr_to_mangatracker_abbr(chapter_data["lang_code"])
            sql = "INSERT INTO chapter_id_to_resource_id(chapter_id, website_id, language_abbr) VALUES (%d, %d, '%s')" \
                  % (mangatracker_chapter_id, Mangadex.website_id_mangadex, language_abbr)
            cursor.execute(sql)
            mangatracker_resource_id = cursor.lastrowid
            logging.info("Resource id for this chapter is %d" % mangatracker_resource_id)
            connection.commit()

            logging.info("Add binding between the resource id %d and the mangadex chapter id %d" % (mangatracker_resource_id, mangadex_chapter_id))
            sql = "INSERT INTO resource_id_to_mangadex_chapter_id(resource_id, mangadex_chapter_id) VALUES (%d, %d)" \
                  % (mangatracker_resource_id, mangadex_chapter_id)
            cursor.execute(sql)
            connection.commit()
