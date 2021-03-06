import logging
from scrapy.crawler import CrawlerProcess
from manga_tracker.database.manga_tracker_database import MangatrackerDatabase
from manga_tracker.database import database_query

MangatrackerDatabase = MangatrackerDatabase()

custom_settings = {
    'LOG_LEVEL': 'CRITICAL',
    'LOG_ENABLED': False
}


class BaseMangaSite:
    base_manga_site = None
    basic_manga_site_database_query = None
    basic_manga_site_spider = None
    process = None

    @classmethod
    def create_table(cls):
        with MangatrackerDatabase.connection.cursor() as cursor:
            cls.basic_manga_site_database_query.create_table_mangatracker_manga_id_to_base_manga_site_manga_id(cursor)
            database_query.insert_new_website(cls.base_manga_site, cursor)

    @classmethod
    def populate_database(cls):
        if cls.process is None:
            BaseMangaSite.process = CrawlerProcess(settings=custom_settings)
        cls.create_table()
        cls.process.crawl(cls.basic_manga_site_spider)

    @classmethod
    def get_full_chapter_url(cls, base_manga_site_manga_id, volume_number, chapter_number):
        return "https://{base_manga_site}.com/comics/%s/%d/%d".format(base_manga_site=cls.base_manga_site) % (
                base_manga_site_manga_id, volume_number, chapter_number)

    @classmethod
    def retrieve_chapter_url(cls, chapter):
        with MangatrackerDatabase.connection.cursor() as cursor:
            logging.info(
                "Retrieving chapter information for resource %d of {base_manga_site}."
                .format(base_manga_site=cls.base_manga_site) % chapter["resource_id"])
            sql = """SELECT {base_manga_site}_manga_id
                     FROM mangatracker_manga_id_to_{base_manga_site}_manga_id
                     WHERE mangatracker_manga_id = %s""".format(base_manga_site=cls.base_manga_site)
            cursor.execute(sql, str(chapter["manga_id"]))
            result = cursor.fetchone()
            manga_id = result["{base_manga_site}_manga_id".format(base_manga_site=cls.base_manga_site)]
            return cls.get_full_chapter_url(manga_id, chapter["volume_number"],
                                            int(chapter["chapter_number"]))
