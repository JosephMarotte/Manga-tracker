from manga_tracker.manga_site.base_manga_site_model.base_manga_site import BaseMangaSite
from manga_tracker.manga_site.base_manga_site_model.base_manga_site_spider import BaseMangaSiteSpider
from manga_tracker.manga_site.base_manga_site_model.base_manga_site_database_query import BaseMangaSiteDatabaseQueryDatabaseQuery

LEVIATANSCANS = "leviatanscans"


class LeviatanscansDatabaseQuery(BaseMangaSiteDatabaseQueryDatabaseQuery):
    base_manga_site = LEVIATANSCANS


class LeviatanscansSpider(BaseMangaSiteSpider):
    name = LEVIATANSCANS
    start_urls = ['https://leviatanscans.com/comics']
    basic_manga_site_database_query = LeviatanscansDatabaseQuery


class Leviatanscans(BaseMangaSite):
    base_manga_site = LEVIATANSCANS
    basic_manga_site_database_query = LeviatanscansDatabaseQuery
    basic_manga_site_spider = LeviatanscansSpider
