
import datetime
from config import LIST_OF_RFC_PAGES, RAW_PAGES_LIST, RFC_BOT_USERNAME, YEARS_TO_PROCESS, site
from pywikibot import Page
from pywikibot.page import Revision
from pywikibot.site import APISite
from pywikibot.diff import html_comparator
from pywikibot.time  import Timestamp
import shelve

from handle_revision import handle_revision


class RevisionRun:
    def __init__(self, year, page_title, timestamp = datetime.datetime.now().timestamp(), comment = '', bot_username = 'Legobot'):
        self.type = 'r-1'
        self.year = year
        self.page_title = page_title
        self.timestamp = timestamp
        self.comment = comment
        self.bot_username = bot_username
        self.revisions_examined = 0
        self.revisions_with_errors = 0

    def get_key(self):
        return f'RevisionRunStart-{self.type}-{self.year}-{self.page_title}-{self.bot_username}-{self.timestamp}'
    
    def increment_revisions_examined(self):
        self.revisions_examined += 1

    def increment_revisions_with_errors(self):
        self.revisions_with_errors += 1
    
    def get_complete_stats(self) -> tuple[str, dict]:
        return (f"RevisionRunStats-{self.type}-{self.year}-{self.page_title}-{self.bot_username}-{self.timestamp}", {
            'revisions_examined': self.revisions_examined,
            'seconds_taken': datetime.datetime.now().timestamp() - self.timestamp,
            'revisions_with_errors': self.revisions_with_errors,
            'type': self.type,
            'year': self.year,
            'bot_username': self.bot_username,
            'page_title': self.page_title,
            'timestamp': self.timestamp,
            'comment': self.comment
        })


def examine_history():

    db = shelve.open('rfc.db', writeback=False)

    for year in YEARS_TO_PROCESS:
        for raw_page_title in RAW_PAGES_LIST:
            page_title = f"Wikipedia:{raw_page_title}"
            bot_username = RFC_BOT_USERNAME
            run = RevisionRun(year=year, page_title=page_title, comment='Examining history for deletions', bot_username=bot_username)    
            db[run.get_key()] = run
            
            try:
                rfc_page = Page(site, page_title)
            except Exception as e:
                db.sync()
                print(f"Error loading page {page_title}: {e}")
                                
            db[run.get_key()] = run

            if isinstance(site, APISite):
                # Seems like we need to use site.loadrevisions to be able to filter by user
                # Loads revisions into the page object
                starttime: Timestamp = Timestamp(year, 1, 1, 0, 0, 0)
                endtime: Timestamp = Timestamp(year + 1, 1, 1, 0, 0, 0)
                history = site.loadrevisions(page=rfc_page, user=bot_username, starttime=starttime, endtime=endtime, rvdir=True)

            # TODO: Do I need to access _revisions or is there a better way?

            # Will print revision entries where the comment contains 'added'
            #  * revid: 1330081275
            # * timestamp: 2025-12-29T10:01:21Z
            # * user: Legobot
            # * comment: Added: [[Talk:Denis Kapustin (militant)]].
            for entry in (rfc_page._revisions or {}).values():
                save_revision(db, run, entry, page_title=page_title, year=year)
            stats_key, stats_value = run.get_complete_stats()
            db[stats_key] = stats_value
            print(f"Completed examining history. Stats: {stats_value}")
            db.sync()
    db.close()

def save_revision(db: shelve.Shelf[any], run: RevisionRun, entry: Revision, page_title: str = '', year: int = 0):
    try:
        processed_key = f"RevisionRunEntryId-{entry.revid}"
        db[processed_key] = False
        db.sync()
        diff_table = site.compare(entry.get('parentid'), entry.get('revid'),'table')
        revision_details = {
            'revid': entry.revid,
            'parentid': entry.parentid,
            'timestamp': entry.timestamp,
            'user': entry.user,
            'comment': entry.comment,
            'diff_table': diff_table,
            'page_title': page_title,
            'bot_username': run.bot_username,
            'year': year
        }
        db[f"RevisionRunEntryDetails-{entry.revid}"] = revision_details
        db[processed_key] = True
        run.increment_revisions_examined()
        print(f"Saved page {page_title} in year {year} revision {entry.revid}")

    # catch any exception
    except Exception as e:
        print(f"Error saving revision {entry.revid}: {e}")
    finally:
        db.sync()
    
    db[run.get_key()] = run

def handle_entry(entry):
    print_keys = ['revid', 'parentid', 'timestamp', 'user', 'comment']
        # added or Removed
    if 'removed' in entry.get('comment', '').lower():
        print_removed_entries(entry, print_keys)


    # TODO: How do I get the diff of what was added/removed in that revision?
    # Maybe site.compare(revid1, revid2) or something like that?

def list_run_stats():
    db = shelve.open('rfc.db', writeback=False)
    year_counts = {}
    for key in db.keys():
        value = db[key]
        if key.startswith('RevisionRunStats-'):
            stats = db[key]
            year = stats.get('year')
            if year not in year_counts:
                year_counts[year] = 0
            year_counts[year] += stats.get('revisions_examined', 0)
            print(f"Stats for {key}: {stats}")
    print("Summary of revisions examined per year:")
    for year, count in year_counts.items():
        print(f"Year {year}: {count} revisions examined")
    db.close()

def list_entry_details():
    db = shelve.open('rfc.db', writeback=False)
    year_counts = {}
    for key in db.keys():
        value = db[key]
        if key.startswith('RevisionRunEntryDetails-'):
            details = db[key]
            handle_revision(details)
            print(f"details for {key}")
    print("Summary of revisions examined per year:")
    for year, count in year_counts.items():
        print(f"Year {year}: {count} revisions examined")
    db.close()
