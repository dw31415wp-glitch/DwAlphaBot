import json
import time

from pywikibot import logging, pagegenerators
from pywikibot.pagegenerators import PageTitleFilterPageGenerator
from pywikibot import page
import pywikibot
from timezone_utils import ensure_utc, now_utc, from_timestamp_utc, to_utc_string
from typing import Dict
import requests
from config import USER_AGENT, EVENT_STREAM_URL, site
from afd_processor import process_afd

TALK = 1

def listen_eventstream():
    recent_changes = pagegenerators.RecentChangesPageGenerator(site)
    # gen = yield_talk_pages(recent_changes)
    gen = filter(is_talk_page, recent_changes)
    for change in gen:
        title = change.title()
        if getattr(change, 'text', '') != '':
            print(f"Recent change: {title} change text: {change.text[:30]}... ")
        else:
            pass

def yield_talk_pages(gen: pagegenerators.GeneratorType):
    for page in gen:
        if page.namespace() == 1:  # Namespace 1 is Talk
            yield page

def is_talk_page(page: pywikibot.Page) -> bool:
    return page.namespace() == TALK

def listen_eventstream3():
    ignore_list: dict[str, dict[str, str]] = {}
    # gen = PageTitleFilterPageGenerator(site.recentchanges, ignore_list=ignore_list)
    gen = pagegenerators.RecentChangesPageGenerator(site)
    for change in gen:
        title = change.title()
        if getattr(change, 'text', '') != '':
            print(f"Recent change: {title} change text: {change.text[:30]}... ")
        else:
            pass
            print(f"Recent change: {title} (exists: {change.exists()})")
        


def listen_eventstream2():
    print("Listening to eventstream...")
    headers = {'User-Agent': USER_AGENT}
    try:
        with requests.get(EVENT_STREAM_URL, headers=headers, stream=True) as response:
            response.raise_for_status()

            # print number of lines received every 30 seconds
            print(f"Connected to eventstream: {EVENT_STREAM_URL}, status code {response.status_code},  length: {response.headers.get('Content-Length')}")

            for line in response.iter_lines():
                if line and line.startswith(b'data: '):
                    #print(f"Received event: {line[6:].decode('utf-8')}")
                    process_event(line[6:].decode('utf-8'))

    except requests.exceptions.RequestException as e:
        print(f"eventstream error: {e}")
        time.sleep(60)
        listen_eventstream()

def process_event(line_data: str):
    try:
        data = json.loads(line_data)

        # if meta.uri does not contain 'en.wikipedia.org', ignore the event
        meta = data.get('meta', {})
        uri = meta.get('uri', '')
        if 'en.wikipedia.org' not in uri or 'Talk' not in uri:
            #print(f"Ignoring non-enwiki event: {uri}")
            return

        # create a page object for the event title
        event_page = pywikibot.Page(site, data.get('title', ''))
        
        print(f"Event page: {event_page.title()} (exists: {event_page.exists()})")
        
        # print pretty JSON of the event data
        
        print(f"Processing event: {data.get('title', 'No Title')}, uri: {uri}")
        logging.debug("Event data: %s", {data.get('title', 'No Title')})
        print(json.dumps(data, indent=2))

        raise NotImplementedError("AfD event processing is currently disabled.")
    
        

        # if is_afd_event(data):
        #     afd_title = data['title']
        #     timestamp = from_timestamp_utc(data['timestamp'])
        #     afd_user = data.get('user', '')
        #     print(f"New AfD: {afd_title}")
        #     process_afd(afd_title, timestamp, afd_user)

    except (json.JSONDecodeError, Exception) as e:
        if isinstance(e, json.JSONDecodeError):
            pass
        else:
            print(f"event processing error: {e}")

def is_afd_event(data: Dict) -> bool:
    title = data.get('title', '')
    return (
        data.get('type') == 'new' and
        data.get('wiki') == 'enwiki' and
        title.startswith('Wikipedia:Articles for deletion/') and
        '/Log/' not in title
    )
