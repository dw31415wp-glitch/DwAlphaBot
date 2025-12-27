import pywikibot

USER_AGENT = 'en:User:Dw31415'
EVENT_STREAM_URL = 'https://stream.wikimedia.org/v2/stream/recentchange'
NOTIFICATION_TEMPLATE = '{{{{subst:User:DwBot/ReviewerAfdNotification|article={article}|afd={afd}}}}}'
OPT_OUT_TEMPLATE = 'User:Dw31415/NoNPPDelivery'
DRY_RUN = True
KILL_PAGE = 'User:Dw31415/kill'

site = pywikibot.Site('test', 'wikipedia')
