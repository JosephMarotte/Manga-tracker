import pymysql.cursors
import functools
from os import path
from manga_tracker.database import database_creation_query


class NoLoginAndPasswordProvidedException(Exception):
    pass


class MangatrackerDatabase:
    class __MangaTrackerDatabase:
        def __init__(self, login, password, database_name="manga_tracker"):
            self.database_name = database_name
            self.connection = pymysql.connect(host='localhost',
                                              user=login,
                                              password=password,
                                              charset='utf8mb4',
                                              cursorclass=pymysql.cursors.DictCursor)
            with self.connection.cursor() as cursor:
                self.create_database(cursor)
                cursor.execute("USE %s" % self.database_name)

        def create_database(self, cursor):
            if not database_creation_query.check_database_exist(self.database_name, cursor):
                database_creation_query.create_database(self.database_name, cursor)
                cursor.execute("USE %s" % self.database_name)
                database_creation_query.create_initial_tables(cursor)

        def close_connection(self):
            self.connection.close()

    instance = None

    def __init__(self, database_name="manga_tracker"):
        self.database_name = database_name

    @property
    @functools.lru_cache()
    def connection(self):
        if not MangatrackerDatabase.instance:
            if not path.exists("manga_tracker_login"):
                login, password = "joseph", "dosaku"
                # raise NoLoginAndPasswordProvidedException
            else:
                with open("manga_tracker_login", "r") as f:
                    login, password = f.read().split()
            MangatrackerDatabase.instance = MangatrackerDatabase.__MangaTrackerDatabase(login, password, self.database_name)
        return self.instance.connection

    @staticmethod
    def set_login_and_password(login, password):
        with open("manga_tracker_login", "w") as f:
            f.write(login + "\n")
            f.write(password)
