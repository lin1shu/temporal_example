import asyncio
import logging
import sys

from temporalio.client import Client
from temporalio.worker import Worker

from activities import say_hello, say_hi, activity_a, activity_b, activity_c, activity_d
from workflow import HelloWorldWorkflow

async def main():
    # Get worker ID from command line or use default
    worker_id = sys.argv[1] if len(sys.argv) > 1 else "1"
    
    # Configure logging with more details
    logging.basicConfig(
        level=logging.INFO,
        format=f'[Worker-{worker_id}] %(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    
    logger = logging.getLogger()
    
    logger.info(f"Worker-{worker_id} is starting up...")
    
    try:
        # Connect client to the running Temporal server
        logger.info("Connecting to Temporal server...")
        client = await Client.connect("localhost:7233")
        logger.info("Successfully connected to Temporal server")
        
        # Create workers based on worker_id
        workers = []
        
        # All workers register for the main workflow and common activities
        logger.info(f"Starting worker on main task queue: new-main-task-queue")
        main_worker = Worker(
            client,
            task_queue="new-main-task-queue",
            workflows=[HelloWorldWorkflow],
            activities=[say_hello, activity_d],  # All workers can handle say_hello and D
        )
        workers.append(main_worker)
        
        # Assign specific activities to specific worker IDs
        if worker_id == "1":
            # Worker 1 handles activity A
            logger.info(f"Worker-1 also handling activity A")
            a_worker = Worker(
                client,
                task_queue="new-activity-a-task-queue",
                activities=[activity_a],
            )
            workers.append(a_worker)
        elif worker_id == "2":
            # Worker 2 handles activity B
            logger.info(f"Worker-2 also handling activity B")
            b_worker = Worker(
                client,
                task_queue="new-activity-b-task-queue",
                activities=[activity_b],
            )
            workers.append(b_worker)
        elif worker_id == "3":
            # Worker 3 handles activity C
            logger.info(f"Worker-3 also handling activity C")
            c_worker = Worker(
                client,
                task_queue="new-activity-c-task-queue",
                activities=[activity_c],
            )
            workers.append(c_worker)
        
        # Worker 5 still handles the say_hi activity
        if worker_id == "5":
            logger.info(f"Worker-5 also handling say_hi activities")
            hi_worker = Worker(
                client,
                task_queue="new-say-hi-task-queue",
                activities=[say_hi],
            )
            workers.append(hi_worker)
        
        # Start all the workers using an async context manager
        async with AsyncExitStack() as stack:
            # Register all workers with the stack
            for worker in workers:
                await stack.enter_async_context(worker)
            
            logger.info(f"Worker-{worker_id} started and ready to process tasks. Ctrl+C to exit.")
            # Wait forever or until interrupted
            await asyncio.Future()
            
    except Exception as e:
        logger.error(f"Error in worker: {e}")
        raise

# Helper class for managing multiple async context managers
class AsyncExitStack:
    def __init__(self):
        self.callbacks = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Execute all callbacks in reverse order
        for callback in reversed(self.callbacks):
            await callback()
        self.callbacks.clear()
    
    async def enter_async_context(self, cm):
        # Enter the context manager and register its exit callback
        result = await cm.__aenter__()
        
        # Register the exit callback
        async def callback():
            await cm.__aexit__(None, None, None)
        
        self.callbacks.append(callback)
        return result

if __name__ == "__main__":
    asyncio.run(main())
