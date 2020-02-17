import scrapy
from manga_tracker.matching_between_website_and_website_id import website_to_website_id
from manga_tracker.database.manga_tracker_database import MangatrackerDatabase
from manga_tracker.database import database_query
from manga_tracker.leviathanscans import levianthanscans_database_query

connection = MangatrackerDatabase().instance.connection


class LeviathanscansSpider(scrapy.Spider):
    name = "leviathanscans"
    start_urls = ['https://leviatanscans.com/comics']

    def parse(self, response):
        for manga_url in response.xpath('//div[@class="media media-comic-card"]/a[@class][@href]/@href').extract():
            yield response.follow(manga_url, callback=self.parse_manga_page)

    def parse_manga_page(self, response):
        with connection.cursor() as cursor:
            leviathanscans_manga_id = response.url.split("/")[-1]
            mangatracker_manga_id = levianthanscans_database_query. \
                select_mangatracker_manga_id_from_leviathanscans_manga_id(leviathanscans_manga_id, cursor)
            if mangatracker_manga_id is None:
                title = response.xpath("//title/text()")[1].extract().lower()
                mangatracker_manga_id = database_query.select_manga_id_of_title(title, cursor)
                if mangatracker_manga_id is None:
                    mangatracker_manga_id = database_query.insert_title(title, cursor)
                levianthanscans_database_query. \
                    insert_mangatracker_manga_id_to_leviathanscans_manga_id(mangatracker_manga_id,
                                                                            leviathanscans_manga_id,
                                                                            cursor)
        # add every chapter to the database
        for chapter_url in response.xpath("//a[contains(text(), 'Chapter')]/@href").extract():
            chapter_url = chapter_url.split("/")
            chapter_data = {'manga_id': mangatracker_manga_id,
                            'volume': chapter_url[-2],
                            'chapter': chapter_url[-1]}
            self.get_chapter_data_to_database(chapter_data)

    def get_chapter_data_to_database(self, chapter_data, check_if_already_in_database=True):
        with connection.cursor() as cursor:
            function_arg = chapter_data['manga_id'], chapter_data['volume'], chapter_data['chapter'], cursor
            mangatracker_chapter_id = database_query.select_chapter_id_from_manga_volume_chapter(*function_arg)
            if mangatracker_chapter_id is None:
                mangatracker_chapter_id = database_query.insert_manga_id_to_chapter_id(*function_arg)

            if check_if_already_in_database:
                function_arg = mangatracker_chapter_id, website_to_website_id[self.name], 'eng', cursor
                if not levianthanscans_database_query.check_if_chapter_already_in_database(*function_arg):
                    database_query.insert_chapter_id_to_resource_id(*function_arg)
