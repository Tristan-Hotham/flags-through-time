"""Manual tables: owner names, Wikidata items for the important entities, and the classes of areas.
Every entry here is a judgement; the page and paper say so. Keys are basemap SUBJECTO strings (after CANON)."""

# Spelling variants and renamings in the basemaps that refer to the same controlling entity.
CANON = {
    "USA": "United States", "United States of America": "United States",
    "UK": "United Kingdom", "United Kingdom of Great Britain and Ireland": "United Kingdom", "GB": "United Kingdom",
    "Manchu Empire": "Qing Empire", "Ming Chinese Empire": "Ming Empire",
    "Neterlands": "Netherlands", "Chinese warlords": "Chinese Warlords", "Kyivan Rus": "Kievan Rus",
    "Maori": "Māori", "Touareg": "Tuareg", "Tuaregs": "Tuareg", "Tuareg Nomadic Tribes": "Tuareg",
    "Athabascan": "Athabaskan", "Samis": "Sámi", "Castille": "Castile", "Austria Hungary": "Austria-Hungary",
    "Austro-Hungarian Empire": "Austria-Hungary", "Spanish Habsburg": "Spain", "Imperial Japan": "Empire of Japan",
    "Khanate of the Golden Horde": "Golden Horde", "Netherlands Indies": "Dutch East Indies", "Polish–Lithuanian Commonwealth": "Poland-Lithuania",
    "Sweden–Norway": "Sweden-Norway", "Tanzania, United Republic of": "Tanzania", "FR": "France",
}

# A trailing "(UK)", "(France)" and so on in a basemap name names the colonial power: the owner becomes that power.
POWER_TAG = {"UK": "United Kingdom", "GB": "United Kingdom", "France": "France", "FR": "France", "Spain": "Spain",
             "Portugal": "Portugal", "Dutch": "Netherlands", "Belgium": "Belgium", "USA": "United States"}

# Wikidata items for the important owners, by period: (first year, last year, [QIDs in order of preference]).
# Flags and arms are then chosen from these items' statements by the rules in 02_match.py.
ITEMS = {
    "United Kingdom": [(1700, 2100, ["Q145", "Q174193", "Q161885"])],
    "England": [(800, 1706, ["Q179876"])], "England and Ireland": [(1500, 1706, ["Q179876"])],
    "Scotland": [(800, 1706, ["Q230791"])],
    "France": [(800, 1791, ["Q70972"]), (1792, 2100, ["Q142"])],
    "Kingdom of France": [(800, 1791, ["Q70972"])],
    "Spain": [(1479, 1700, ["Q170603", "Q29"]), (1701, 2100, ["Q29"])],
    "Portugal": [(1100, 2100, ["Q45"])],
    "Netherlands": [(1580, 1794, ["Q170072", "Q55"]), (1795, 2100, ["Q55", "Q29999"])],
    "Qing Empire": [(1636, 1912, ["Q8733"])],
    "Ming Empire": [(1368, 1644, ["Q9903"])],
    "Mughal Empire": [(1526, 1857, ["Q33296"])],
    "Holy Roman Empire": [(962, 1806, ["Q12548"])],
    "Venice": [(697, 1797, ["Q4948"])],
    "Ottoman Empire": [(1299, 1922, ["Q12560"])],
    "Russian Empire": [(1721, 1917, ["Q34266"])],
    "Tsardom of Muscovy": [(1547, 1721, ["Q186096"])],
    "Grand Duchy of Moscow": [(1263, 1547, ["Q1751483"])],
    "Russia": [(1914, 1917, ["Q34266"]), (1991, 2100, ["Q159"])],
    "USSR": [(1922, 1991, ["Q15180"])],
    "White Russia": [], "Far Eastern SSR": [],
    "United States": [(1776, 2100, ["Q30"])],
    "China": [(1912, 1949, ["Q13426199", "Q865"]), (1949, 2100, ["Q148"])],
    "Taiwan": [(1945, 2100, ["Q865"])],
    "Empire of Japan": [(1868, 1947, ["Q188712"])],
    "Japan": [(1947, 2100, ["Q17"])],
    "Tokugawa shogunate": [(1603, 1867, ["Q205662"])],
    "Austrian Empire": [(1650, 1867, ["Q131964"])],
    "Austria-Hungary": [(1867, 1918, ["Q28513"])],
    "Prussia": [(1525, 1933, ["Q38872"])],
    "German Empire": [(1871, 1918, ["Q43287"])],
    "Germany": [(1871, 1945, ["Q183", "Q43287"]), (1946, 2100, ["Q183"])],
    "Italy": [(1861, 2100, ["Q38"])],
    "Kingdom of Italy": [(1861, 1946, ["Q172579"])],
    "Denmark-Norway": [(1500, 1814, ["Q62651"])],
    "Poland-Lithuania": [(1569, 1795, ["Q172107"])],
    "Persia": [(1789, 1925, ["Q63158027"])],
    "Safavid Empire": [(1501, 1736, ["Q18234383"])], "Timurid Empire": [(1370, 1507, ["Q484195"])],
    "Korea, Republic of": [(1948, 2100, ["Q884"])], "Korea, Democratic People's Republic of": [(1948, 2100, ["Q423"])],
    "Byelarus": [(1991, 2100, ["Q184"])], "Gambia, The": [(1965, 2100, ["Q1005"])],
    "Georgia": [(1000, 1490, ["Q154667"]), (1491, 1990, []), (1991, 2100, ["Q230"])],
    "Greenland": [(1900, 1984, ["Q35"]), (1985, 2100, ["Q223"])],
    "Kingdom of Brazil": [(1815, 1889, ["Q3932042", "Q155"])],
    "Joseon": [(1392, 1897, ["Q28179"])], "Korea": [(1392, 1897, ["Q28179"])],
    "Mexico": [(1810, 2100, ["Q96"])], "Canada": [(1867, 2100, ["Q16"])],
    "India": [(1947, 2100, ["Q668"])], "Iran": [(1920, 2100, ["Q794"])],
    "Sweden": [(900, 2100, ["Q34"])], "Denmark": [(900, 2100, ["Q35"])], "Norway": [(900, 2100, ["Q20"])],
    "Morocco": [(700, 1914, []), (1915, 2100, ["Q1028"])], "Ethiopia": [(1270, 2100, ["Q115", "Q207521"])],
    "Brazil": [(1889, 2100, ["Q155"])], "Australia": [(1901, 2100, ["Q408"])],
    "Union of South Africa": [(1910, 1961, ["Q193619"])], "South Africa": [(1961, 2100, ["Q258"])],
    "Mongol Empire": [(1206, 1368, ["Q12557"])], "Byzantine Empire": [(395, 1453, ["Q12544"])],
    "Inca Empire": [(1438, 1572, ["Q28573"])], "Aztec Empire": [(1428, 1521, ["Q12542"])],
    "Maratha Confederacy": [(1674, 1818, ["Q83618"])], "Sultanate of Delhi": [(1206, 1526, ["Q174710"])],
    "Golden Horde": [(1240, 1502, ["Q79965"])],
    "Abbasid Caliphate": [(750, 1258, ["Q12536"])], "Carolingian Empire": [(800, 888, ["Q81287"])],
    "Kalmar Union": [(1397, 1523, ["Q62623"])], "Viceroyalty of New Spain": [(1521, 1821, ["Q170603"])],
    "Viceroyalty of the Río de la Plata": [(1776, 1814, ["Q170603"])],
    "British East India Company": [(1600, 1874, ["Q83164"])],
    "Dutch East Indies": [(1800, 1949, ["Q55"])],
}

# Owners that are peoples, cultural regions or loose groups rather than one state. Shown hatched, with their name.
# Matched as whole words in the owner name (lower case); see is_people() in 02_match.py for the full rule.
PEOPLE_WORDS = ["hunter", "gatherer", "peoples", "tribes", "farmers", "nomad", "cultures", "foragers", "fishers", "fichers",
                "herders", "pastoralists", "chiefdoms", "city-states", "hunters", "warlords", "states", "kingdoms", "khanates",
                "emirates", "principalities", "confederacies", "clans", "settlements", "sultanates"]
PEOPLE = {"Siberians", "Bantu peoples", "Khoisan", "Thule", "Dorset", "Inuit", "Tupis", "Mandes", "Azandes", "Berbers", "Arabs",
          "Bedouins", "Uyghurs", "Mongols", "Tuareg", "Papuans", "Papu", "Ainu", "Māori", "Sámi", "Cree", "Athabaskan", "Tungus",
          "Malay", "Malays", "Malagasy", "Oghuz Turks", "Karluks", "Khitans", "Permians", "Oromo", "Chukchi", "Koryaks",
          "Anasazi", "Mogollon", "Taino", "Beothuk", "Innu", "Polynesians", "Melanesians", "Micronesians", "Aborigines",
          "Turkic peoples", "Slavs", "Germanic peoples", "Celts", "Baltic peoples", "Finns", "Lapps", "Pechenegs",
          "Cumans", "Kipchaks", "Magyars", "Avars", "Samoyeds", "Yakuts", "Evenks", "Turan", "Arabia", "Dënéndeh",
          "Očhéthi Šakówiŋ", "Michif Piyii (Métis)", "Tekohá (Guarani)", "T'atsaot'ine", "Peshemegs", "Plains Indians",
          "Ainus", "Sami", "Bulgars", "Karelians", "Northmen", "Bashkirs", "Nenets", "Nganasan", "Itelmen", "Beja people", "Cushites",
          "Shona", "Akan", "Zulu", "Maoris", "Oghuz", "Sikhs", "Rajputs", "Cholas", "Senas", "Pratiharas", "Chauhans", "Slavic tribes",
          "Baltic tribes", "Ciboney", "Boethuk", "Lozi", "Barotse", "Yeke", "Luba", "Lunda"}
# Owner names that contain one of PEOPLE_WORDS but are a single state.
NOT_PEOPLE = {"United States", "Papal States", "Hausa States", "Mossi States", "Shan states", "Malaysian Islamic states",
              "Federated Malay States", "Trucial States", "Confederate States of America", "Orange Free State", "Congo Free State",
              "Irish Free State", "Free State of Fiume", "Emirate of Bin Shal'an", "Rupert's Land", "Hawaiian Kingdom",
              "Mexihcah (Triple Alliance)", "Tarascan state", "Chimú", "Muisca", "Purépecha"}
STATE_WORDS = ["empire", "kingdom", "sultanate", "caliphate", "khanate", "emirate", "republic", "duchy", "principality", "dynasty",
               "union", "tsardom", "shogunate", "viceroyalty", "colony", "colonies", "protectorate", "company", "horde", "khaganate",
               "federation", "raj", "commonwealth", "mandate", "dominion", "confederation", "imamate", "order", "state", "territory",
               "county", "margraviate", "electorate", "march", "despotate", "beylik", "ssr", "alliance", "league"]

# Present-day flags missing from the downloaded Commons set, filled from the flag-icons project (MIT licence; the flag
# designs themselves are public domain). Start years are the years of adoption.
EXTRA = {
    "Q148": {"lab": "People's Republic of China", "inc": 1949, "file": "Flag of the People's Republic of China.svg", "code": "cn", "start": 1949},
    "Q423": {"lab": "North Korea", "inc": 1948, "file": "Flag of North Korea.svg", "code": "kp", "start": 1948},
}

# Flags with no dates in Wikidata but a well-documented early use (start year from each flag's Wikipedia article).
# Used only for the rule "a present-day flag is shown from this year on" instead of the default (1900).
KNOWN_SINCE = {
    "Flag of Denmark.svg": (1400, "the Dannebrog is shown in the Gelre Armorial of the 1370s to 1380s"),
    "Flag of Sweden.svg": (1600, "the blue and yellow cross was in use by the 16th century, though fixed in law only in 1906"),
}
