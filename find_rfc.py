

from pywikibot import Page
from config import LIST_OF_RFC_PAGES, site

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

        # collect the list of links on the page
        links = list_page.linkedPages()
        links = list(filter(is_not_other_list_page, links))
        links = list(filter(is_not_user_page, links))

        for linked_page in links:
            print(f"    - {linked_page.title()}")

        for link in list_page.langlinks():
            print(f"    - Langlink: {link}")
