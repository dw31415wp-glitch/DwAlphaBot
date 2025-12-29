
import asyncio

import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode
from pywikibot import Link

from config import MAX_RFC_PAGES_TO_PROCESS
from find_rfc import RfcStats, get_rfc_list

class RfcSectionQueue():
    def __init__(self):
        self.queue = asyncio.Queue(5)

    async def put(self, item: tuple[Wikicode, str, Link]) -> None:
        # get the size and print it
        size = self.queue.qsize()
        print (f"RfcSectionQueue size before put: {size}")
        await self.queue.put(item)

    async def get(self) -> tuple[Wikicode, str, Link]:
        rfc_info = await self.queue.get()
        return rfc_info
    
class RfcStatsQueue():
    def __init__(self):
        self.queue = asyncio.Queue(5)

    async def put(self, item: tuple[RfcStats, str, Link]) -> None:
        # get the size and print it
        size = self.queue.qsize()
        print (f"RfcStatsQueue size before put: {size}")
        await self.queue.put(item)

    async def get(self) -> tuple[RfcStats, str, Link]:
        # get item from queue and return
        stats = await self.queue.get()
        return stats
    

async def calculate_rfc_stats(rfc_queue: RfcSectionQueue, rfc_stats_queue: RfcStatsQueue) -> None:
    print ("Waiting for RFC section to process...")
    rfc_section, rfc_id, link = await rfc_queue.get()
    print (f"Processing RFC ID: {rfc_id}, Link: {link}")
    stats = RfcStats()
    stats.link = link

    # publish fake status for demo purposes
    stats.user_counts = {"UserA": 3, "UserB": 1}
    print (f"Calculated stats for RFC ID: {rfc_id}, Link: {link}, User counts: {stats.user_counts}")
    await rfc_stats_queue.put((stats, rfc_id, link))
    rfc_queue.queue.task_done()

async def collect_results(rfc_stats_queue: RfcStatsQueue) -> list[tuple[RfcStats, str, Link]]:
    results: list[tuple[RfcStats, str, Link]] = []
    while True:
        try:
            # use the underlying queue's non-blocking API to drain
            stats, rfc_id, link = rfc_stats_queue.queue.get_nowait()
            results.append((stats, rfc_id, link))
        except asyncio.QueueEmpty:
            break
    return results

        
async def analyze_rfcs():
    # create a queue of RFCs to analyze
    rfc_queue = RfcSectionQueue()
    rfc_stats_queue = RfcStatsQueue()

    # Start producer and consumer as concurrent tasks
    producer_task = asyncio.create_task(get_rfc_list(rfc_queue))
    
    # Run consumer workers concurrently
    consumer_tasks = [
        asyncio.create_task(calculate_rfc_stats(rfc_queue, rfc_stats_queue))
        for _ in range(MAX_RFC_PAGES_TO_PROCESS)
    ]
    
    # Wait for all to complete or timeout
    try:
        await asyncio.gather(producer_task, *consumer_tasks)
    except Exception as e:
        print(f"Error: {e}")
    
    results: list[tuple[RfcStats, str, Link]] = await collect_results(rfc_stats_queue)
    return results



