CREATE TABLE website_to_id_website
(
  website_id TINYINT UNSIGNED NOT NULL,
  website_name VARCHAR(256) NOT NULL,
  PRIMARY KEY (website_id),
  UNIQUE (website_id)
);

CREATE TABLE manga_id_to_english_title
(
  manga_id MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,
  title VARCHAR(256) NOT NULL,
  PRIMARY KEY (manga_id),
  UNIQUE (title)
);

CREATE TABLE manga_id_to_chapter_id
(
    manga_id MEDIUMINT UNSIGNED NOT NULL,
    chapter_id MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,
    volume_number MEDIUMINT unsigned,
    chapter_number DECIMAL(5, 1) NOT NULL,
    PRIMARY KEY (chapter_id),
    UNIQUE (manga_id, chapter_id),
    UNIQUE (manga_id, volume_number, chapter_number),
    FOREIGN KEY (manga_id) REFERENCES manga_id_to_english_title(manga_id)
);

-- A same chapter (same volume and same chapter) may be stored multiple time (ie : language / website)
CREATE TABLE chapter_id_to_resource_id
(
    resource_id MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,
    chapter_id MEDIUMINT UNSIGNED NOT NULL,
    website_id TINYINT UNSIGNED NOT NULL,
    language_abbr CHAR(3) NOT NULL, -- using iso 639-3 abbreviation
    PRIMARY KEY (resource_id),
    FOREIGN KEY (chapter_id) REFERENCES manga_id_to_chapter_id(chapter_id),
    FOREIGN KEY (website_id) REFERENCES website_to_id_website(website_id)
);

-- Table specific to retrieve the resource on different trackers
-- Tables specific to mangadex
CREATE TABLE manga_id_mangadex_to_manga_id_mangatracker
(
  manga_id_mangatracker MEDIUMINT UNSIGNED NOT NULL,
  manga_id_mangadex MEDIUMINT UNSIGNED NOT NULL,
  PRIMARY KEY(manga_id_mangatracker),
  FOREIGN KEY(manga_id_mangatracker) REFERENCES manga_id_to_english_title(manga_id),
  UNIQUE (manga_id_mangadex)
);

CREATE TABLE resource_id_to_mangadex_chapter_id
(
    resource_id MEDIUMINT UNSIGNED NOT NULL,
    mangadex_chapter_id MEDIUMINT UNSIGNED NOT NULL,
    PRIMARY KEY (mangadex_chapter_id),
    FOREIGN KEY (resource_id) REFERENCES chapter_id_to_resource_id(resource_id),
    UNIQUE (resource_id)
);
