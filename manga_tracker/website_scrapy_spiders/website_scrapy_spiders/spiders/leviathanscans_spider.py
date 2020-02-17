import scrapy
import logging
from manga_tracker.matching_between_website_and_website_id import website_to_website_id
from manga_tracker.database.manga_tracker_database import MangatrackerDatabase

connection = MangatrackerDatabase().instance.connection


class LeviathanscansSpider(scrapy.Spider):
    name = "leviathanscans"
    start_urls = ['https://leviatanscans.com/comics']

    def parse(self, response):
        for manga_url in response.xpath('//div[@class="media media-comic-card"]/a[@class][@href]/@href').extract():
            yield response.follow(manga_url, callback=self.parse_manga_page)

    def parse_manga_page(self, response):
        leviathanscans_manga_id = response.url.split("/")[-1]

        logging.info("Checking whether leviathanscans manga %s is in our database" % leviathanscans_manga_id)
        with connection.cursor() as cursor:
            sql = """SELECT mangatracker_manga_id
                     FROM mangatracker_manga_id_to_leviathanscans_manga_id
                     WHERE leviathanscans_manga_id LIKE '%s'""" % leviathanscans_manga_id
            cursor.execute(sql)
            mangatracker_manga_id = cursor.fetchone()
            if mangatracker_manga_id is None:
                logging.info("Leviathanscans manga %s is not in our database" % leviathanscans_manga_id)
                logging.info("Adding leviathanscans manga %s to our database" % leviathanscans_manga_id)
                title = response.xpath("//title/text()")[1].extract().lower()
                logging.info("Checking whether title %s is in our database", title)
                sql = """SELECT manga_id
                         FROM manga_id_to_english_title
                         WHERE title LIKE %s"""
                cursor.execute(sql, title)
                mangatracker_manga_id = cursor.fetchone()

                if mangatracker_manga_id is None:
                    logging.info("The title %s is not in our database, adding it to the database" % title)
                    sql = """INSERT INTO manga_id_to_english_title(title) VALUES (%s)"""
                    cursor.execute(sql, title)
                    mangatracker_manga_id = cursor.lastrowid
                    connection.commit()
                    logging.info("The title %s has been added to the database with id %d"
                                 % (title, mangatracker_manga_id))
                else:  # unwrap needed
                    mangatracker_manga_id = mangatracker_manga_id["manga_id"]
                logging.info("Adding matching between mangatracker_manga_id %d and leviathanscans_manga_id %s"
                             % (mangatracker_manga_id, leviathanscans_manga_id))
                sql = "INSERT INTO mangatracker_manga_id_to_leviathanscans_manga_id(mangatracker_manga_id, leviathanscans_manga_id) \
                       VALUES (%s, %s)"
                cursor.execute(sql, (mangatracker_manga_id, leviathanscans_manga_id))
                connection.commit()
                logging.info("Matching between mangatracker_manga_id %d and leviathanscans_manga_id %s was added"
                             % (mangatracker_manga_id, leviathanscans_manga_id))
            else:
                logging.info("Leviathanscans manga %s is already in our database" % leviathanscans_manga_id)
                mangatracker_manga_id = mangatracker_manga_id["mangatracker_manga_id"]

        # add every chapter to the database
        for chapter_url in response.xpath("//a[contains(text(), 'Chapter')]/@href").extract():
            chapter_url = chapter_url.split("/")
            chapter_data = {'manga_id': mangatracker_manga_id,
                            'volume': chapter_url[-2],
                            'chapter': chapter_url[-1]}
            self.get_chapter_data_to_database(chapter_data)

    def get_chapter_data_to_database(self, chapter_data, check_if_already_in_database=True):
        logging.info("Check if there is a mangatracker_chapter_id for this chapter")  # TODO

        with connection.cursor() as cursor:
            sql = """SELECT chapter_id
                     FROM manga_id_to_chapter_id
                     WHERE manga_id = %s AND
                           volume_number = %s AND
                           chapter_number = %s
                           """
            cursor.execute(sql, (chapter_data['manga_id'], chapter_data['volume'], chapter_data['chapter']))
            mangatracker_chapter_id = cursor.fetchone()
            if mangatracker_chapter_id is None:
                logging.info("There was no mangatracker chapter_id for this chapter, adding it to the database")  # TODO
                sql = "INSERT INTO manga_id_to_chapter_id(manga_id, volume_number, chapter_number) VALUES (%s, %s, %s)"
                cursor.execute(sql, (chapter_data['manga_id'], chapter_data['volume'], chapter_data['chapter']))
                connection.commit()
                logging.info("Mangatracker chapter_id for this chapter was added to the database")  # TODO
                mangatracker_chapter_id = cursor.lastrowid
            else:
                mangatracker_chapter_id = mangatracker_chapter_id["chapter_id"] # unwrap

        if check_if_already_in_database:
            # On leviathanscans only one same chapter for a specific manga
            sql = """SELECT 1
                     FROM chapter_id_to_resource_id
                     WHERE chapter_id = %s AND
                           website_id = %s AND
                           language_abbr = %s"""
            with connection.cursor() as cursor:
                cursor.execute(sql, (str(mangatracker_chapter_id), str(website_to_website_id[self.name]), 'eng'))
                result = cursor.fetchone()
                if result is not None:
                    logging.info("This chapter is already in the database")
                    return
        with connection.cursor() as cursor:
            sql = """INSERT INTO chapter_id_to_resource_id(chapter_id, website_id, language_abbr) VALUES (%s, %s, %s)"""
            cursor.execute(sql, (str(mangatracker_chapter_id), str(website_to_website_id[self.name]), 'eng'))
            connection.commit()
