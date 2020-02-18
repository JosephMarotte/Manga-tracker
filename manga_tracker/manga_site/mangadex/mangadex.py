import requests
import json
import logging
from manga_tracker.manga_site.mangadex.mangadex_utils import mangadex_abbr_to_mangatracker_abbr
from manga_tracker.database.manga_tracker_database import MangatrackerDatabase
from manga_tracker.database import database_query
from manga_tracker.manga_site.mangadex import mangadex_database_query

connection = MangatrackerDatabase().instance.connection

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
        with connection.cursor() as cursor:
            resource_id = chapter["resource_id"]
            mangadex_chapter_id = mangadex_database_query.select_mangadex_chapter_id_from_resource_id(resource_id,
                                                                                                      cursor)
            return Mangadex.get_full_chapter_url(mangadex_chapter_id)

    @staticmethod
    def get_title_data(mangadex_manga_id):
        # TODO add error case with the code
        r = requests.get(Mangadex.get_full_title_api_url(mangadex_manga_id), auth=('users', 'pass'))

        manga_data = json.loads(r.text)
        title = manga_data['manga']['title'].lower()

        # check whether the mangadex title exists or not
        with connection.cursor() as cursor:
            if not mangadex_database_query.check_if_mangadex_manga_id_is_in_database(mangadex_manga_id, cursor):
                mangatracker_manga_id = database_query.select_manga_id_of_title(title, cursor)
                if mangatracker_manga_id is None:
                    mangatracker_manga_id = database_query.insert_title(title, cursor)
                mangadex_database_query.insert_mangatracker_manga_id_to_mangadex_manga_id(mangatracker_manga_id,
                                                                                          mangadex_manga_id,
                                                                                          cursor)

        print("ici")
        for str_mangadex_chapter_id in manga_data['chapter']:
            chapter_data = manga_data['chapter'][str_mangadex_chapter_id]
            chapter_data['manga_id'] = mangadex_manga_id
            mangadex_chapter_id = int(str_mangadex_chapter_id) # int(str_mangadex_chapter_id)  # from str to int
            Mangadex.get_chapter_data_to_database(mangadex_chapter_id, True, chapter_data)

    @staticmethod
    def get_chapter_data_to_database(mangadex_chapter_id, check_if_already_in_database=True, chapter_data=None):
        """ Retrieving chapter data when we read manga data with the API """
        with connection.cursor() as cursor:
            if check_if_already_in_database:
                if mangadex_database_query.check_if_mangadex_chapter_id_is_in_database(mangadex_chapter_id, cursor):
                    return

            if chapter_data is None:
                logging.info("Retrieving chapter data of chapter %d" % mangadex_chapter_id)
                r = requests.get(Mangadex.get_full_chapter_api_url(mangadex_chapter_id), auth=('users', 'pass'))
                chapter_data = json.loads(r.text)
                logging.info("Chapter data of chapter %d were retrieved" % mangadex_chapter_id)

            # In some case volume and chapter are empty (for example for oneshots). Artificially build it.
            if chapter_data['volume'] == "":
                chapter_data['volume'] = '1'
            if chapter_data['chapter'] == "":
                chapter_data['chapter'] = '1'

            mangadex_manga_id = chapter_data['manga_id']

            # Retrieve the mangatracker_manga_id
            # TODO in some case we already computed manga_id_mangatracker from reading the manga, we may not recompute
            # TODO it but only pass it as an argument to the function
            mangatracker_manga_id = \
                mangadex_database_query.select_mangatracker_manga_id_from_mangadex_manga_id(mangadex_manga_id, cursor)

            # Retrieve mangatracker_chapter_id for this chapter
            function_arg = mangatracker_manga_id, chapter_data['volume'], chapter_data['chapter'], cursor
            mangatracker_chapter_id = database_query.select_chapter_id_from_manga_volume_chapter(*function_arg)

            if mangatracker_chapter_id is None:
                mangatracker_chapter_id = database_query.insert_manga_id_to_chapter_id(*function_arg)
            language_abbr = mangadex_abbr_to_mangatracker_abbr(chapter_data["lang_code"])
            function_arg = mangatracker_chapter_id, Mangadex.website_id_mangadex, language_abbr, cursor
            mangatracker_resource_id = database_query.insert_chapter_id_to_resource_id(*function_arg)
            mangadex_database_query.insert_mangatracker_resource_id_to_mangadex_chapter_id(mangatracker_resource_id,
                                                                                           mangadex_chapter_id,
                                                                                           cursor)
