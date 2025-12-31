
from config import LIST_OF_RFC_PAGES, site
from pywikibot import Page
from pywikibot.site import APISite


def examine_history():

    rfc_page = Page(site, LIST_OF_RFC_PAGES[0])

    if isinstance(site, APISite):
        # Seems like we need to use site.loadrevisions to be able to filter by user
        # Loads revisions into the page object
        history = site.loadrevisions(page=rfc_page, total=10, user='Legobot')

    # TODO: Do I need to access _revisions or is there a better way?

    # Will print revision entries where the comment contains 'added'
    #  * revid: 1330081275
    # * timestamp: 2025-12-29T10:01:21Z
    # * user: Legobot
    # * comment: Added: [[Talk:Denis Kapustin (militant)]].
    for entry in (rfc_page._revisions or {}).values():
        print_keys = ['revid', 'timestamp', 'user', 'comment']
        for key in print_keys:
            if 'added' in entry.get('comment', '').lower():
                print(f"* {key}: {entry.get(key)}")

    # TODO: How do I get the diff of what was added/removed in that revision?
    # Maybe site.compare(revid1, revid2) or something like that?
