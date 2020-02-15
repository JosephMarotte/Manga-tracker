mangadex_code_to_iso639_3 = {
    'sa': 'ara',  # Arabic
    'bd': 'ben',  # Bengali
    'bg': 'bul',  # Bulgarian
    'mm': 'mya',  # Burmese
    'ct': 'cat',  # Catalan
    'cn': 'zho',  # Chinese (Simple)
    'hk': 'yue',  # Chinese (Traditional)
    'cz': 'ces',  # Czech
    'dk': 'dan',  # Danish
    'dk': 'dan',  # Danish
    'nl': 'nld',  # Dutch
    'gb': 'eng',  # English
    'ph': 'fil',  # Filipino
    'fi': 'fin',  # Finnish
    'fr': 'fra',  # French
    'de': 'deu',  # German
    'gr': 'ell',  # Greek
    'il': 'heb',  # Hebrew
    'hu': 'hun',  # Hungarian
    'id': 'ind',  # Indonesian
    'it': 'ita',  # Italian
    'jp': 'jpn',  # Japanese
    'kr': 'kor',  # Korean
    'lt': 'lit',  # Lithuanian
    'my': 'msa',  # Malay
    'mn': 'mon',  # Mongolian
    'ir': 'fas',  # Persian
    'pl': 'pol',  # Polish
    'br': 'por',  # Portuguese (Brazil)
    'pt': 'por',  # Portuguese (Portugal)
    'ro': 'ron',  # Romanian
    'ru': 'rus',  # Russian
    'rs': 'hbs',  # Serbo-Croatian
    'es': 'spa',  # Spanish (Spain)
    'mx': 'spa',  # Spanish (Latin America)
    'se': 'swe',  # Swedish
    'th': 'tha',  # Thai
    'tr': 'tur',  # Turkish
    'ua': 'ukr',  # Ukrainian
    'vn': 'vie'  # Vietnamese
}


def mangadex_abbr_to_mangatracker_abbr(mangadex_code):
    return mangadex_code_to_iso639_3[mangadex_code]
