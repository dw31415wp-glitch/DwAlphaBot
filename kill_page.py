import pywikibot
from config import site, KILL_PAGE

def check_kill_page():
    try:
        kill_page = pywikibot.Page(site, KILL_PAGE)
        print(f"Checking kill page: {KILL_PAGE}")
        if kill_page.exists() and 'kill' in kill_page.text.lower():
            print("Kill page detected. Shutting down bot.")
            return True
    except Exception as e:
        print(f"Error checking kill page: {e}")
    return False