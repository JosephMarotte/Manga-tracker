from manga_tracker.manga_site.base_manga_site_model.base_manga_site import BaseMangaSite
from manga_tracker.manga_site.base_manga_site_model.base_manga_site_spider import BaseMangaSiteSpider
from manga_tracker.manga_site.base_manga_site_model.base_manga_site_database_query import BaseMangaSiteDatabaseQueryDatabaseQuery

ZEROSCANS = "zeroscans"


class ZeroscansDatabaseQuery(BaseMangaSiteDatabaseQueryDatabaseQuery):
    base_manga_site = ZEROSCANS


class ZeroscansSpider(BaseMangaSiteSpider):
    name = ZEROSCANS
    start_urls = ['https://zeroscans.com/comics']
    basic_manga_site_database_query = ZeroscansDatabaseQuery


class Zeroscans(BaseMangaSite):
    base_manga_site = "zeroscans"
    basic_manga_site_database_query = ZeroscansDatabaseQuery
    basic_manga_site_spider = ZeroscansSpider
