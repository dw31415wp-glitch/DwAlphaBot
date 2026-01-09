
import argparse
import asyncio
import time
from threading import Thread

from pywikibot import Page
import analyze_rfcs
from config import DRY_RUN, site, LIST_OF_RFC_PAGES, JOB_TO_RUN
from find_rfc import get_rfc_list
from kill_page import check_kill_page
from event_handler import listen_eventstream
from examine_history import examine_history, list_entry_details, list_run_stats
#from examine_history import examine_history
#from notification_processor import process_pending_notifications

SENTINEL = None

valid_jobs = ['analyze_rfcs', 'examine_history', 'list_entry_details', 'list_run_stats']

def main():

    parser = argparse.ArgumentParser(description='Run the RFC Bot with specified job.')
    parser.add_argument('-j', '--job', type=str, choices=valid_jobs, default=JOB_TO_RUN,
                        help='The job to run. Options: analyze_rfcs, examine_history, list_entry_details, list_run_stats')
    args = parser.parse_args()

    # get_rfc_list()
    
    if args.job == 'analyze_rfcs':
        asyncio.run(analyze_rfcs.analyze_rfcs())

    if args.job == 'examine_history':
        #list_run_stats()
        list_entry_details()
        #examine_history()

    # exit for now
    return

    print(f"starting AfD bot (Dry run: {DRY_RUN})")
    # Thread(target=listen_eventstream, daemon=True).start()
    start_time = time.time()
    cycle_count = 0

    listen_eventstream()

    while True and cycle_count < 1:
        if check_kill_page():
            pass
        else:
            print("Bot is running...")
            #listen_eventstream()
            time.sleep(30)
            #process_pending_notifications()
            # stop after 10 seconds for demo purposes
            if time.time() - start_time > 10:
                print("Stopping bot after demo period.")
                break
        time.sleep(500)
        cycle_count += 1

if __name__ == '__main__':
    main()
