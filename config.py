import pywikibot

USER_AGENT = 'en:User:Dw31415'
EVENT_STREAM_URL = 'https://stream.wikimedia.org/v2/stream/recentchange'
NOTIFICATION_TEMPLATE = '{{{{subst:User:DwBot/ReviewerAfdNotification|article={article}|afd={afd}}}}}'
OPT_OUT_TEMPLATE = 'User:Dw31415/NoNPPDelivery'
DRY_RUN = False
KILL_PAGE = 'User:Dw31415/kill'
RESULTS_PAGE = 'https://en.wikipedia.org/wiki/User:DwAlphaBot/RfcEditStats'
RESULT_PAGE_TITLE = 'User:DwAlphaBot/RfcEditStats'
RAW_PAGES_LIST = [
  "Requests_for_comment/Biographies",
  "Requests_for_comment/Economy,_trade,_and_companies",
  "Requests_for_comment/History_and_geography",
  "Requests_for_comment/Language_and_linguistics",
  "Requests_for_comment/Maths,_science,_and_technology",
  "Requests_for_comment/Media,_the_arts,_and_architecture",
  "Requests_for_comment/Politics,_government,_and_law",
  "Requests_for_comment/Religion_and_philosophy",
  "Requests_for_comment/Society,_sports,_and_culture",
  "Requests_for_comment/Wikipedia_style_and_naming",
  "Requests_for_comment/Wikipedia_policies_and_guidelines",
  "Requests_for_comment/WikiProjects_and_collaborations",
  "Requests_for_comment/Wikipedia_technical_issues_and_templates",
  "Requests_for_comment/Wikipedia_proposals",
  "Requests_for_comment/Unsorted",
  "Requests_for_comment/User_names"
]


# Article topics (View all)
# Biographies	{{rfc|bio}}
# Economy, trade, and companies	{{rfc|econ}}
# History and geography	{{rfc|hist}}
# Language and linguistics	{{rfc|lang}}
# Maths, science, and technology	{{rfc|sci}}
# Media, the arts, and architecture	{{rfc|media}}
# Politics, government, and law	{{rfc|pol}}
# Religion and philosophy	{{rfc|reli}}
# Society, sports, and culture	{{rfc|soc}}
# Project-wide topics (View all)
# Wikipedia style and naming	{{rfc|style}}
# Wikipedia policies and guidelines	{{rfc|policy}}
# WikiProjects and collaborations	{{rfc|proj}}
# Wikipedia technical issues and templates	{{rfc|tech}}
# Wikipedia proposals	{{rfc|prop}}
# Unsorted
# Unsorted RfCs	{{rfc}}

RAW_PAGES_DICT = {
    'BIO': 'Requests_for_comment/Biographies',
    'ECON': 'Requests_for_comment/Economy,_trade,_and_companies',
    'HIST': 'Requests_for_comment/History_and_geography',
    'LANG': 'Requests_for_comment/Language_and_linguistics',
    'SCI': 'Requests_for_comment/Maths,_science,_and_technology',
    'MEDIA': 'Requests_for_comment/Media,_the_arts,_and_architecture',
    'POL': 'Requests_for_comment/Politics,_government,_and_law',
    'RELI': 'Requests_for_comment/Religion_and_philosophy',
    'SOC': 'Requests_for_comment/Society,_sports,_and_culture',
    'STYLE': 'Requests_for_comment/Wikipedia_style_and_naming',
    'POLICY': 'Requests_for_comment/Wikipedia_policies_and_guidelines',
    'PROJ': 'Requests_for_comment/WikiProjects_and_collaborations',
    'TECH': 'Requests_for_comment/Wikipedia_technical_issues_and_templates',
    'PROP': 'Requests_for_comment/Wikipedia_proposals',
    'UNSORTED': 'Requests_for_comment/Unsorted',
    'USERNAMES': 'Requests_for_comment/User_names'
}

LIST_OF_RFC_PAGES = [
    'Wikipedia:Requests for comment/Politics, government, and law'
]

RFC_BOT_USERNAME = 'Legobot' # or 'RFC Bot' # or 'Legobot'

#YEARS_TO_PROCESS = [2022, 2023]
# process 10 years up until 2021
YEARS_TO_PROCESS = [2024, 2025]
# list(range(2012, 2022))
MAX_RFC_PAGES_TO_PROCESS = 5
JOB_TO_RUN = 'examine_history'  # Options: 'analyze_rfcs', 'examine_history'


site = pywikibot.Site('en', 'wikipedia')
