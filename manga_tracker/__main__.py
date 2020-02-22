import argparse
import logging
from manga_tracker.database.manga_tracker_database import MangatrackerDatabase
from manga_tracker.users.users import Users
from manga_tracker.users.create_feed_from_manga_list import create_feed
from manga_tracker.manga_site.manga_website_name_to_website_class import get_class_of_website
from manga_tracker.manga_site.base_manga_site_model.base_manga_site import BaseMangaSite

# command name
create_user = "create_user"
set_database_login_password = "set_database_login_password"
change_language_pref_order = "change_language_pref_order"
change_website_pref_order = "change_website_pref_order"
add_followed_manga = "add_followed_manga"
populate_database = "populate_database"
retrieve_followed_manga = "retrieve_followed_manga"

# args name
command = "command"
user_id = "user_id"
output_file = "output_file"
language_pref_order = "language_pref_order"
website_pref_order = "website_pref_order"
title_or_manga_id_list = "title_or_manga_id_list"
website_name_list = "website_name_list"
login = "login"
password = "password"


parser = argparse.ArgumentParser(prog='manga_tracker')
subparsers = parser.add_subparsers(dest=command)
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")


parser_create_user = subparsers.add_parser(create_user, help="Create a new user")

parser_set_database_login_password = subparsers.add_parser(set_database_login_password, help="Set login and password for the database")
parser_set_database_login_password.add_argument(login)
parser_set_database_login_password.add_argument(password)

parser_change_language_pref_order = subparsers.add_parser(change_language_pref_order, help="Change language preference for a user")
parser_change_language_pref_order.add_argument(user_id)
parser_change_language_pref_order.add_argument(language_pref_order, nargs='+')

parser_change_website_pref_order = subparsers.add_parser(change_website_pref_order, help="Change website preference for a user")
parser_change_website_pref_order.add_argument(user_id)
parser_change_website_pref_order.add_argument(website_pref_order, nargs='+')

parser_add_followed_manga = subparsers.add_parser(add_followed_manga, help="Add new followed manga for a user")
parser_add_followed_manga.add_argument(user_id)
parser_add_followed_manga.add_argument(title_or_manga_id_list, nargs='+')

parser_retrieve_followed_manga = subparsers.add_parser(retrieve_followed_manga, help="Retrieve followed manga for a user")
parser_retrieve_followed_manga.add_argument(user_id)
parser_retrieve_followed_manga.add_argument(output_file)

parser_populate_database = subparsers.add_parser(populate_database, help="Retrieve update of the website to the internal database")
parser_populate_database.add_argument(website_name_list, nargs='*')


def main():
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.disable(50)

    if args.command == create_user:
        u = Users()
        print("Your user id is {}".format(u.user_id))
    elif args.command == set_database_login_password:
        MangatrackerDatabase.set_login_and_password(args.login, args.password)
    elif args.command == change_language_pref_order:
        u = Users(args.user_id)
        u.rank_language_pref(args.language_pref_order)
    elif args.command == change_website_pref_order:
        u = Users(args.user_id)
        u.rank_website_name_pref(args.website_pref_order)
    elif args.command == add_followed_manga:
        u = Users(args.user_id)
        u.add_new_followed_manga_list(args.title_or_manga_id_list)
    elif args.command == retrieve_followed_manga:
        u = Users(args.user_id)
        followed_manga = u.retrieve_followed_manga()
        create_feed(followed_manga, args.output_file)
    elif args.command == populate_database:
        for website_name in args.website_name_list:
            website_class = get_class_of_website(website_name)
            if website_class:
                website_class.populate_database()
            else:
                print("Website {} is not in not handled by our project yet".format(website_name))
        # TODO can only have one process.start() for the crawler, try to do this in cleaner way
        if BaseMangaSite.process is not None:
            BaseMangaSite.process.start()


if __name__ == '__main__':
    main()
