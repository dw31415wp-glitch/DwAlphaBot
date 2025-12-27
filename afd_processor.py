import re
from datetime import datetime
from typing import Optional
import mwparserfromhell
import pywikibot
from timezone_utils import ensure_utc, now_utc, from_timestamp_utc, to_utc_string
from config import site
#from reviewer_finder import get_reviewers
#from notification_storage import save_pending_notification

def process_afd(afd_title: str, afd_timestamp: datetime, afd_user: str = None):
    try:
        afd_page = pywikibot.Page(site, afd_title)

        if not afd_page.exists():
            print(f"AfD page missing: {afd_title}")
            return

        article_title = extract_article_title(afd_page.text)
        if not article_title:
            print(f"cannot extract article title from: {afd_title}")
            return

        print(f"Afded article: {article_title}")
        #reviewers = get_reviewers(article_title, afd_timestamp, afd_user)
        reviewers = None

        if not reviewers:
            print(f"no reviewers found for: {article_title}")
            return

        #save_pending_notification(afd_title, article_title, afd_timestamp, reviewers)

    except Exception as e:
        print(f"AfD processing error '{afd_title}': {e}")

def extract_article_title(wikitext: str) -> Optional[str]:
    try:
        wikicode = mwparserfromhell.parse(wikitext)

        for template in wikicode.filter_templates():
            name = template.name.strip().lower()
            if name == 'la' and template.has(1):
                return str(template.get(1).value).strip()

        for section in wikicode.get_sections(flat=True, include_lead=False, include_headings=True):
            for heading in section.filter_headings():
                text = heading.title.strip()
                match = re.search(r'\[\[:?(.*?)\]\]', text)
                if match:
                    return match.group(1).strip()

    except Exception as e:
        print(f"title extraction error: {e}")

    return None
