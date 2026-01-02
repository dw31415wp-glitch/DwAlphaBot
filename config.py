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

LIST_OF_RFC_PAGES = [
    'Wikipedia:Requests for comment/Politics, government, and law'
]

RFC_BOT_USERNAME = 'Legobot'

YEARS_TO_PROCESS = [2022, 2023]
MAX_RFC_PAGES_TO_PROCESS = 5
JOB_TO_RUN = 'examine_history'  # Options: 'analyze_rfcs', 'examine_history'


site = pywikibot.Site('en', 'wikipedia')
