import argparse
from manga_tracker.users.users import Users
from manga_tracker.users.users import Users
from manga_tracker.users.create_feed_from_manga_list import create_feed
from manga_tracker.manga_site.manga_website_name_to_website_class import get_class_of_website
from scrapy.crawler import CrawlerProcess
from manga_tracker.manga_site.zeroscans.zeroscans import ZeroscansSpider
from manga_tracker.manga_site.leviatanscans.leviatanscans import LeviatanscansSpider


# from scrapy.crawler import CrawlerProcess
# from manga_tracker.manga_site.zeroscans.zeroscans import ZeroscansSpider
# process = CrawlerProcess()
# print("ici")
# process.crawl(LeviatanscansSpider)
# # process.crawl(ZeroscansSpider)
# process.start()
#
# a = Users(10)
# a.add_new_followed_manga(140)
# a.rank_website_pref([3, 2, 1])
# a.rank_language_pref(['eng'])
# r = a.retrieve_followed_manga()
# s = create_feed(r)

#Mangadex.get_title_data(7139)
#pprint(r)
# pprint(s)
#print(len(r))

# command name
create_user = "create_user"
change_language_pref_order = "change_language_pref_order"
change_website_pref_order = "change_website_pref_order"
add_followed_manga = "add_followed_manga"
populate_database = "populate_database"
retrieve_followed_manga = "retrieve_followed_manga"

# args name
command = "command"
user_id = "user_id"
output_file = "output_file"

parser = argparse.ArgumentParser()
parser.add_argument(command)
args, remaining = parser.parse_known_args()

if args.command == create_user:
    u = Users()
    print("Your user id is {}".format(u.user_id))
elif args.command == change_language_pref_order:
    parser.add_argument(user_id)
    args, language_pref_order = parser.parse_known_args()
    u = Users(args.user_id)
    u.rank_language_pref(language_pref_order)
elif args.command == change_website_pref_order:
    parser.add_argument(user_id)
    args, website_pref_order = parser.parse_known_args()
    u = Users(args.user_id)
    u.rank_website_pref(website_pref_order)
elif args.command == add_followed_manga:
    parser.add_argument(user_id)
    args, title_or_manga_id_list = parser.parse_known_args()
    u = Users(args.user_id)
    u.add_new_followed_manga_list(title_or_manga_id_list)
elif args.command == retrieve_followed_manga:
    parser.add_argument(user_id)
    parser.add_argument(output_file)
    args = parser.parse_args()
    u = Users(args.user_id)
    followed_manga = u.retrieve_followed_manga()
    create_feed(followed_manga, args.output_file)
elif args.command == populate_database:
    website_name_list = remaining
    for website_name in website_name_list:
        website_class = get_class_of_website(website_name)
        if website_class:
            website_class.populate_database()
        else:
            print("Website {} is not in not handled by our project yet".format(website_name))


