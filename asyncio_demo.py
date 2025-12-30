import asyncio
import random
import time

# Sentinel value to signal end of production
SENTINEL = None

async def producer(queue, num_items):
    """Generates items and puts them in the queue."""
    for i in range(num_items):
        item = f"item-{i}"
        await asyncio.sleep(random.uniform(0.1, 0.5)) # Simulate async I/O work
        await queue.put(item)
        print(f"Produced {item}")

    # Add a sentinel for each consumer to signal completion
    for _ in range(3): # Assuming 3 consumers
        await queue.put(SENTINEL)
    print("Producer finished")

async def consumer(queue, name):
    """Consumes items from the queue and processes them."""
    while True:
        item = await queue.get()
        if item is SENTINEL:
            print(f"Consumer {name} received sentinel, shutting down.")
            queue.task_done()
            break
        
        print(f"Consumer {name} processing {item}")
        await asyncio.sleep(random.uniform(0.1, 0.3)) # Simulate async I/O work
        print(f"Consumer {name} finished {item}")
        queue.task_done() # Mark the task as done

async def main():
    """Main function to set up producer and consumers."""
    queue = asyncio.Queue()
    num_items = 10
    
    # Create producer task
    producer_task = asyncio.create_task(producer(queue, num_items))
    
    # Create consumer tasks (e.g., 3 consumers)
    consumers = [asyncio.create_task(consumer(queue, f"C{i}")) for i in range(1, 4)]
    
    # Wait for the producer to finish
    await producer_task
    
    # Wait for all items in the queue to be processed
    await queue.join()

    # Cancel remaining consumer tasks that are now idle (after processing sentinels)
    for c in consumers:
        c.cancel()
    
    # Gracefully handle cancellations
    await asyncio.gather(*consumers, return_exceptions=True)
    print("All tasks finished.")

if __name__ == "__main__":
    asyncio.run(main())
