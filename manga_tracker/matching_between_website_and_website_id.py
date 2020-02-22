from manga_tracker.database.manga_tracker_database import MangatrackerDatabase


class WebsiteMatching:
    get_table_query = """SELECT * from website_to_id_website"""

    dict_loaded = False

    _website_to_website_id = {}
    _website_id_to_website = {}

    @property
    def website_to_website_id(self):
        WebsiteMatching.update_dict()
        return WebsiteMatching._website_to_website_id

    @property
    def website_id_to_website(self):
        WebsiteMatching.update_dict()
        return WebsiteMatching._website_id_to_website

    @classmethod
    def update_dict(cls):
        if not cls.dict_loaded:
            cls.dict_loaded = True
            with MangatrackerDatabase().connection.cursor() as cursor:
                cursor.execute(cls.get_table_query)
                result = cursor.fetchall()
                for e in result:
                    website_id = e["website_id"]
                    website_name = e["website_name"]
                    cls._website_to_website_id[website_name] = website_id
                    cls._website_id_to_website[website_id] = website_name

    @classmethod
    def add_website(cls, website, website_id):
        cls._website_id_to_website[website_id] = website
        cls._website_to_website_id[website] = website_id

    @classmethod
    def next_id(cls):
        cls.update_dict()
        return len(cls._website_id_to_website) + 1
