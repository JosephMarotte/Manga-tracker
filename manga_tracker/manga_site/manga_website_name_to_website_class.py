from manga_tracker.manga_site.leviatanscans.leviatanscans import Leviatanscans
from manga_tracker.manga_site.zeroscans.zeroscans import Zeroscans
from manga_tracker.manga_site.reaperscans.reaperscans import Reaperscans
from manga_tracker.manga_site.mangadex.mangadex import Mangadex


def get_class_of_website(website_name):
    class_name = website_name.title()
    try:
        return globals()[class_name]
    except KeyError:
        return None
