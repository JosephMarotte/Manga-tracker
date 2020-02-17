import pymysql.cursors
import logging

# TODO not have password / users hardcoded. And handle connection in a better way
connection = pymysql.connect(host='localhost',
                             user='joseph',
                             password='dosaku',
                             db='manga_tracker',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


LEVIATHANSCANS = "leviathanscans"


# TODO change name from leviathan to leviatan
class Leviathanscans:
    @staticmethod
    def get_full_chapter_url(leviathanscans_manga_id, volume_number, chapter_number):
        return "https://leviatanscans.com/comics/%s/%d/%d" % (leviathanscans_manga_id, volume_number, chapter_number)

    @staticmethod
    def retrieve_chapter_url(chapter):
        with connection.cursor() as cursor:
            logging.info("Retrieving chapter information for resource %d of leviathanscans." % chapter["resource_id"])
            sql = """SELECT leviathanscans_manga_id
                     FROM mangatracker_manga_id_to_leviathanscans_manga_id
                     WHERE mangatracker_manga_id = %s"""
            cursor.execute(sql, str(chapter["manga_id"]))
            result = cursor.fetchone()
            leviathanscans_manga_id = result["leviathanscans_manga_id"]
            return Leviathanscans.get_full_chapter_url(leviathanscans_manga_id, chapter["volume_number"], int(chapter["chapter_number"]))
