from manga_tracker.manga_site.base_manga_site_model.base_manga_site import BaseMangaSite
from manga_tracker.manga_site.base_manga_site_model.base_manga_site_spider import BaseMangaSiteSpider
from manga_tracker.manga_site.base_manga_site_model.base_manga_site_database_query import BaseMangaSiteDatabaseQueryDatabaseQuery

REAPERSCANS = "reaperscans"


class ReaperscansDatabaseQuery(BaseMangaSiteDatabaseQueryDatabaseQuery):
    base_manga_site = REAPERSCANS


class ReaperscansSpider(BaseMangaSiteSpider):
    name = REAPERSCANS
    start_urls = ['https://reaperscans.com/comics']
    basic_manga_site_database_query = ReaperscansDatabaseQuery


class Reaperscans(BaseMangaSite):
    base_manga_site = REAPERSCANS
    basic_manga_site_database_query = ReaperscansDatabaseQuery
    basic_manga_site_spider = ReaperscansSpider
