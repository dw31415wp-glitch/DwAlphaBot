
import asyncio

import mwparserfromhell
from mwparserfromhell.wikicode import Wikicode
from pywikibot import Link, Page

from asyncio_demo import SENTINEL
from calculate_statistics import calculate_statistics
from config import MAX_RFC_PAGES_TO_PROCESS, RESULT_PAGE_TITLE, site
from find_rfc import RfcStats, get_rfc_list
from stats_publisher import draft_report, publish_report


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
        self.queue = asyncio.Queue()

    async def put(self, item: tuple[RfcStats, str, Link]) -> None:
        # get the size and print it
        size = self.queue.qsize()
        print (f"RfcStatsQueue size before put: {size}")
        await self.queue.put(item)

    async def get(self) -> tuple[RfcStats, str, Link]:
        # get item from queue and return
        stats = await self.queue.get()
        return stats
    

async def calculate_rfc_stats_worker(rfc_queue: RfcSectionQueue, rfc_stats_queue: RfcStatsQueue, worker_id: int) -> None:
    """Worker that continuously processes items from queue until None is received (sentinel)."""
    calculated_count = 0
    while True:
        print(f"[Worker {worker_id}] Waiting for RFC section...")
        await asyncio.sleep(0)  # Yield control
        rfc_section, rfc_id, link = await rfc_queue.get()
        
        # Sentinel value: None signals end of input
        if rfc_section is None:
            print(f"[Worker {worker_id}] Received sentinel, exiting")
            rfc_queue.queue.task_done()
            break
        
        print(f"[Worker {worker_id}] Processing RFC ID: {rfc_id}, Link: {link}")
        stats = RfcStats()
        stats.link = link

        # publish fake status for demo purposes
        stats.user_counts = calculate_statistics(rfc_section)
        print(f"[Worker {worker_id}] {calculated_count} Calculated stats for RFC ID: {rfc_id}, Link: {link}, User counts: {stats.user_counts}")
        await asyncio.sleep(0)  # Yield control
        await rfc_stats_queue.put((stats, rfc_id, link))
        rfc_queue.queue.task_done()
        calculated_count += 1

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

async def queue_status_monitor(rfc_queue: RfcSectionQueue, rfc_stats_queue: RfcStatsQueue) -> None:
    """Periodically prints the sizes of the queues."""
    while True:
        rfc_queue_size = rfc_queue.queue.qsize()
        rfc_stats_queue_size = rfc_stats_queue.queue.qsize()
        print(f"[Queue Monitor] RFC Section Queue size: {rfc_queue_size}, RFC Stats Queue size: {rfc_stats_queue_size}")
        await asyncio.sleep(5)  # Adjust the interval as needed
        
async def analyze_rfcs():
    # create a queue of RFCs to analyze



    rfc_queue = RfcSectionQueue()
    rfc_stats_queue = RfcStatsQueue()

    # Start producer as a task
    producer_task = asyncio.create_task(get_rfc_list(rfc_queue))
    consumer_task = asyncio.create_task(calculate_rfc_stats_worker(rfc_queue, rfc_stats_queue, 1))
    # Start queue status monitor
    monitor_task = asyncio.create_task(queue_status_monitor(rfc_queue, rfc_stats_queue))

    # Wait for the producer to finish
    await producer_task

    print("Producer finished, waiting for all items to be processed...")
    
    # Wait for all items in the queue to be processed
    await rfc_queue.queue.join()
    consumer_task.cancel()
    monitor_task.cancel()

    # collect status
    results: list[tuple[RfcStats, str, Link]] = await collect_results(rfc_stats_queue)
    content = draft_report(results)
    publish_report(content, RESULT_PAGE_TITLE)

    # test read result page title from config
    


    return results

    print("All items processed, sending sentinels to workers...")
    
    # # Start multiple consumer workers (each runs a loop until sentinel)
    # num_workers = 3
    # consumer_tasks = [
    #     asyncio.create_task(calculate_rfc_stats_worker(rfc_queue, rfc_stats_queue, i))
    #     for i in range(num_workers)
    # ]
    
    # # Wait for producer to finish, then wait for all queued items to be processed
    # await producer_task
    # print("Producer finished, waiting for all items to be processed...")
    # await rfc_queue.queue.join()  # blocks until all task_done() calls match put() calls
    
    # print("All items processed, sending sentinels to workers...")
    # for _ in range(num_workers):
    #     await rfc_queue.put((None, None, None))
    
    # # Wait for all workers to finish
    # await asyncio.gather(*consumer_tasks)
    
    # results: list[tuple[RfcStats, str, Link]] = await collect_results(rfc_stats_queue)
    # return results



