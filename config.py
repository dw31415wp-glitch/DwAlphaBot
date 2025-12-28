import pywikibot

USER_AGENT = 'en:User:Dw31415'
EVENT_STREAM_URL = 'https://stream.wikimedia.org/v2/stream/recentchange'
NOTIFICATION_TEMPLATE = '{{{{subst:User:DwBot/ReviewerAfdNotification|article={article}|afd={afd}}}}}'
OPT_OUT_TEMPLATE = 'User:Dw31415/NoNPPDelivery'
DRY_RUN = True
KILL_PAGE = 'User:Dw31415/kill'
RESULTS_PAGE = 'https://en.wikipedia.org/wiki/User:DwAlphaBot/RfcEditStats'
LIST_OF_RFC_PAGES = [
    'Wikipedia:Requests for comment/Politics, government, and law'
]
MAX_RFC_PAGES_TO_PROCESS = 5


site = pywikibot.Site('en', 'wikipedia')
