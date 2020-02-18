import logging
from manga_tracker.database.manga_tracker_database import MangatrackerDatabase

connection = MangatrackerDatabase().instance.connection


class BaseMangaSite:
    base_manga_site = None

    @classmethod
    def get_full_chapter_url(cls, base_manga_site_manga_id, volume_number, chapter_number):
        return "https://{base_manga_site}.com/comics/%s/%d/%d".format(base_manga_site=cls.base_manga_site) % (
                base_manga_site_manga_id, volume_number, chapter_number)

    @classmethod
    def retrieve_chapter_url(cls, chapter):
        with connection.cursor() as cursor:
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
