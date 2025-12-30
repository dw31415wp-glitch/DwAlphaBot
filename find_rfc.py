

import asyncio
from pywikibot import Link, Page
from config import LIST_OF_RFC_PAGES, MAX_RFC_PAGES_TO_PROCESS, site
from typing import List, Tuple
import mwparserfromhell

def is_not_other_list_page(page: Page) -> bool:
    other_list_pages = [
        "Wikipedia:Requests for comment",
    ]
    # Return True if the page title is not in the other list pages
    in_list = False
    for other_page in other_list_pages:
        if other_page.lower() in page.title().lower():
            in_list = True
            break
    return not in_list

def is_not_user_page(page: Page) -> bool:
    return not page.title().startswith("User")

def get_links_from_text(page: Page) -> List[Tuple[Page, Link]]:
    import pywikibot
    from pywikibot import textlib

    result_set = set()
    results = []

    rfc_number = 0

    for m in pywikibot.link_regex.finditer(textlib.removeDisabledParts(page.text)):
        link = pywikibot.Link(m["title"], site)
        try:
            anchor = m.groupdict().get("label") or ""
            rfc_page = Page(site, link.title, link.namespace)
            print(f"  (page exists: {rfc_page.title} {rfc_page.exists()})")
            if rfc_page.exists():
                if rfc_page in result_set:
                    continue
                result_set.add(rfc_page)
                results.append((rfc_page, link))
                rfc_number += 1
                if rfc_number >= MAX_RFC_PAGES_TO_PROCESS:
                    print(f"Reached max RFC pages to process. {len(results)} pages collected.")
                    return results

        except Exception as e:
            print(f"Error processing link {m} {link}: {e}")
            raise e

    return results

def get_sections_from_page(page: Page, rfc_id: str) -> mwparserfromhell.wikicode.Wikicode | None:
    """Return list of sections as dicts: {'heading': str, 'text': str}.

    Uses mwparserfromhell when available; falls back to a regex-based splitter.
    """
    text = page.text or ""

    # Try mwparserfromhell first for robust parsing
    try:
        wikicode = mwparserfromhell.parse(text)
        sections = []
        for sec in wikicode.get_sections(include_lead=False):
            if rfc_id not in str(sec).lower():
                continue
            headings = sec.filter_headings()
            heading = str(headings[0].title).strip() if headings else ""    
            return sec
        return None
    except Exception:
        # Fallback: crude regex-based section split
        import re

        pattern = re.compile(r"(?m)^(={2,})\s*(.+?)\s*\1\s*$")
        matches = list(pattern.finditer(text))
        if not matches:
            return [{"heading": "", "text": text}]

        sections = []
        last_end = 0
        last_heading = ""
        for m in matches:
            start = m.start()
            if last_end < start:
                body = text[last_end:start]
                if last_heading or body.strip():
                    sections.append({"heading": last_heading, "text": body})
            last_heading = m.group(2).strip()
            last_end = m.end()

        # append trailing part
        if last_end < len(text):
            sections.append({"heading": last_heading, "text": text[last_end:]})

        return sections
    
class RfcStats:
    def __init__(self):
        self.link: Link | None = None
        self.user_counts: dict[str, int] = {}

def calculate_rfc_stats(rfc_section: mwparserfromhell.wikicode.Wikicode, rfc_id: str, link: Link) -> RfcStats:
    """Calculate stats for a given RFC section."""
    stats = RfcStats()
    stats.link = link

    # Count user mentions in the section
    for links in rfc_section:
        pass

    return stats

async def get_rfc_list(rfc_queue) -> None:
    print("RFC Pages to monitor:")
    for page in LIST_OF_RFC_PAGES:
        print(f"- {page}")
        list_page = Page(site, page)
        if list_page.exists():
            print(f"  (Page exists)")
        else:
            print(f"  (Page does not exist)")
        
        # print the initial content of the page
        print(f"  Content preview: {list_page.text[:50]}...")

        results = []

        rfc_page_results = get_links_from_text(list_page)
        for result in rfc_page_results:
            rfc_page, link = result
            target_rfc = link.section or "*******No section linked*****"
            # for section like rfc ABD0AB3
            # extract the id after 'rfc '
            rfc_id = ""
            if 'rfc ' in target_rfc.lower():
                rfc_id = target_rfc.lower().split('rfc ')[1].strip()
            # if no id found, skip
            if rfc_id == "":
                continue
            
            rfc_section = get_sections_from_page(rfc_page, rfc_id)
            if rfc_section is not None:
                print(f"Putting in queue: {rfc_page.title()} (Link: {link})")
                await rfc_queue.put((rfc_section, rfc_id, link))
                # Yield control to allow workers to process
                await asyncio.sleep(0)
                # results.append(calculate_rfc_stats(rfc_section, rfc_id, link))
            else:
                print(f"      No matching section found for RFC ID: {rfc_id}")
                continue
            # collect the list of links on the page
        # collect the list of links on the page
        # links = list_page.linkedPages()
        # links = list(filter(is_not_other_list_page, links))
        # links = list(filter(is_not_user_page, links))

        # for linked_page in links:
        #     print(f"    - {linked_page.title()}")

        # for link in list_page.langlinks():
        #     print(f"    - Langlink: {link}")
