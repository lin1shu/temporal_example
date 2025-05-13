import asyncio
import logging
import sys

from temporalio.client import Client
from temporalio.worker import Worker

from activities import say_hello
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
    
        # Run a worker for the workflow
        logger.info(f"Starting worker on task queue: hello-world-task-queue")
        async with Worker(
            client,
            task_queue="hello-world-task-queue",
            workflows=[HelloWorldWorkflow],
            activities=[say_hello],
        ):
            # Worker runs until shut down
            logger.info(f"Worker-{worker_id} started and ready to process tasks. Ctrl+C to exit.")
            await asyncio.Future()
    except Exception as e:
        logger.error(f"Error in worker: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 