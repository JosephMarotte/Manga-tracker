# Element should always be added at the bottom of the list to not change the order of the previous elements
# TODO remove dummy_website by re-initializing database and having mangadex having id = 0
website_names = [
                "dummy_website",
                "mangadex",
                "leviatanscans",
                "zeroscans"
                ]

name_already_seen = set()
unique_website_name = []
for website_name in website_names:
    if website_name not in name_already_seen:
        unique_website_name.append(website_name)
        name_already_seen.add(website_name)

website_names = unique_website_name

website_id_to_website = {i: website_name for (i, website_name) in enumerate(website_names)}
website_to_website_id = {website_name: i for (i, website_name) in enumerate(website_names)}
