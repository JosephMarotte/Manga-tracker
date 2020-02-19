from feedgen.feed import FeedGenerator
from manga_tracker.matching_between_website_and_website_id import website_id_to_website
from manga_tracker.manga_site.manga_website_name_to_website_class import get_class_of_website


# Manga list returned by retrieve_followed_manga
def create_feed(chapter_list, output_file):
    fg = FeedGenerator()
    fg.title("Manga chapter you haven't read yet")
    fg.link(href='http://example.com', rel='alternate')
    fg.description("Manga chapter you haven't read yet, you have {} chapters to read".format(len(chapter_list)))
    fg.language("en")

    for chapter in chapter_list:
        build_feed_entry(fg, chapter)
    fg.rss_file(output_file)
    return fg


def build_feed_entry(fg, chapter):
    # retrieve the website and its class the chapter belongs to
    class_name = website_id_to_website[chapter["website_id"]]
    website_class = get_class_of_website(class_name)

    # build chapter link from the website class
    chapter_link = website_class.retrieve_chapter_url(chapter)

    # build entry for the feeder
    fe = fg.add_entry()
    fe.id(str(chapter["chapter_id"]))
    fe.title(build_title(chapter))
    fe.link(href=chapter_link)


def build_title(chapter):
    return "%s volume %d chapter %s" % (chapter["title"], chapter["volume_number"], chapter["chapter_number"])
