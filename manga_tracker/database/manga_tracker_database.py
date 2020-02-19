import pymysql.cursors
from manga_tracker.database import database_creation_query


class MangatrackerDatabase:
    database_name = "manga_tracker"

    class __MangaTrackerDatabase:
        def __init__(self, database_name="manga_tracker"):
            self.database_name = database_name
            self.connection = pymysql.connect(host='localhost',
                                              user='joseph',
                                              password='dosaku',
                                              charset='utf8mb4',
                                              cursorclass=pymysql.cursors.DictCursor)
            with self.connection.cursor() as cursor:
                self.create_database(cursor)
                sql_query = "USE %s" % self.database_name
                cursor.execute(sql_query)

        def create_database(self, cursor):
            if not database_creation_query.check_database_exist(self.database_name, cursor):
                database_creation_query.create_database(self.database_name, cursor)

        def close_connection(self):
            self.connection.close()

    instance = None

    def __init__(self, database_name="manga_tracker"):
        if not MangatrackerDatabase.instance:
            MangatrackerDatabase.instance = MangatrackerDatabase.__MangaTrackerDatabase(database_name)
