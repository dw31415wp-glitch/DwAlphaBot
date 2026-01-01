
from config import LIST_OF_RFC_PAGES, site
from pywikibot import Page
from pywikibot.site import APISite
from pywikibot.diff import html_comparator
from pywikibot.time  import Timestamp


def examine_history():

    rfc_page = Page(site, LIST_OF_RFC_PAGES[0])

    if isinstance(site, APISite):
        # Seems like we need to use site.loadrevisions to be able to filter by user
        # Loads revisions into the page object
        starttime: Timestamp = Timestamp(2024, 1, 1, 0, 0, 0)
        endtime: Timestamp = Timestamp(2025, 1, 1, 0, 0, 0)
        history = site.loadrevisions(page=rfc_page, user='Legobot', starttime=starttime, endtime=endtime, rvdir=True)

    # TODO: Do I need to access _revisions or is there a better way?

    # Will print revision entries where the comment contains 'added'
    #  * revid: 1330081275
    # * timestamp: 2025-12-29T10:01:21Z
    # * user: Legobot
    # * comment: Added: [[Talk:Denis Kapustin (militant)]].
    for entry in (rfc_page._revisions or {}).values():
        print_keys = ['revid', 'parentid', 'timestamp', 'user', 'comment']
        # added or Removed
        if 'removed' in entry.get('comment', '').lower():
            comment = entry.get('comment')
            # Delete everything before "[["
            if "[[" in comment:
                comment = comment[comment.index("[["):]
            # remove any trailing period
            if comment.endswith('.'):
                comment = comment[:-1]

            print(f'== {comment} ==')
            revision_comment = '<!-- dwalphabot=1,'
            for key in print_keys:
                #print(f"* {key}: {entry.get(key)}")
                revision_comment += f"{key}={str(entry.get(key))},"
            revision_comment += ' -->\n'
            print(revision_comment)
            diff_table = site.compare(entry.get('parentid'), entry.get('revid'),'table') # works better than 'inline'
            diff_compare = html_comparator(diff_table)

            deleted_content = diff_compare['deleted-context'] or []
            deleted_lines = '\n'.join(deleted_content)

            print(deleted_lines)
            print("")



    # TODO: How do I get the diff of what was added/removed in that revision?
    # Maybe site.compare(revid1, revid2) or something like that?
