import pymysql.cursors


# singleton design pattern
class MangatrackerDatabase:
    class __MangaTrackerDatabase:
        def __init__(self):
            # TODO not have password / users hardcoded. And handle connection in a better way
            self.connection = pymysql.connect(host='localhost',
                                              user='joseph',
                                              password='dosaku',
                                              db='manga_tracker',
                                              charset='utf8mb4',
                                              cursorclass=pymysql.cursors.DictCursor)

        def close_connection(self):
            self.connection.close()

    instance = None

    def __init__(self):
        if not MangatrackerDatabase.instance:
            MangatrackerDatabase.instance = MangatrackerDatabase.__MangaTrackerDatabase()
