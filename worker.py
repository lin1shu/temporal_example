import asyncio
import logging
import sys

from temporalio.client import Client
from temporalio.worker import Worker

from activities import say_hello, say_hi
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
        
        # All workers register the workflow and say_hello activity
        logger.info(f"Starting worker on main task queue: hello-world-task-queue")
        main_worker = Worker(
            client,
            task_queue="hello-world-task-queue",
            workflows=[HelloWorldWorkflow],
            activities=[say_hello],
        )
        
        # Only worker-5 gets an additional worker listening on the say-hi queue
        if worker_id == "5":
            logger.info(f"Worker-5 also starting dedicated worker for say_hi activities")
            hi_worker = Worker(
                client,
                task_queue="say-hi-task-queue",
                activities=[say_hi],
            )
            # Start both workers
            async with main_worker, hi_worker:
                logger.info(f"Worker-{worker_id} started and ready to process tasks. Ctrl+C to exit.")
                await asyncio.Future()
        else:
            # Start just the main worker for all other worker IDs
            async with main_worker:
                logger.info(f"Worker-{worker_id} started and ready to process tasks. Ctrl+C to exit.")
                await asyncio.Future()
            
    except Exception as e:
        logger.error(f"Error in worker: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 