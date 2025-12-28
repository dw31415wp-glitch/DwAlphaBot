

from pywikibot import Link, Page
from config import LIST_OF_RFC_PAGES, MAX_RFC_PAGES_TO_PROCESS, site
from typing import List, Tuple

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

    results = []

    rfc_number = 0

    for m in pywikibot.link_regex.finditer(textlib.removeDisabledParts(page.text)):
        link = pywikibot.Link(m["title"], site)
        try:
            anchor = m.groupdict().get("label") or ""
            rfc_page = Page(site, link.title, link.namespace)
            print(f"  (exists: {rfc_page.exists()})")
            if rfc_page.exists():
                results.append((rfc_page, link))
                rfc_number += 1
                if rfc_number >= MAX_RFC_PAGES_TO_PROCESS:
                    print("Reached max RFC pages to process.")
                    return results

        except Exception as e:
            print(f"Error processing link {m} {link}: {e}")
            raise e

    return results


def get_sections_from_page(page: Page) -> list:
    """Return list of sections as dicts: {'heading': str, 'text': str}.

    Uses mwparserfromhell when available; falls back to a regex-based splitter.
    """
    text = page.text or ""

    # Try mwparserfromhell first for robust parsing
    try:
        import mwparserfromhell

        wikicode = mwparserfromhell.parse(text)
        sections = []
        for sec in wikicode.get_sections(include_lead=False):
            headings = sec.filter_headings()
            heading = str(headings[0].title).strip() if headings else ""
            sections.append({"heading": heading, "text": str(sec)})
        return sections
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
        
def get_rfc_list():
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

        rfc_page_results = get_links_from_text(list_page)
        for result in rfc_page_results:
            rfc_page, link = result
            print(f"    - {rfc_page.title()} (Link: {link})")
            sections = get_sections_from_page(rfc_page)
            for sec in sections:
                print(f"      Section: {sec['heading'][:30]}... Text preview: {sec['text'][:30]}...")

        # collect the list of links on the page
        # links = list_page.linkedPages()
        # links = list(filter(is_not_other_list_page, links))
        # links = list(filter(is_not_user_page, links))

        # for linked_page in links:
        #     print(f"    - {linked_page.title()}")

        # for link in list_page.langlinks():
        #     print(f"    - Langlink: {link}")
