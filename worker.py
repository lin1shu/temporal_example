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
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=f'[Worker-{worker_id}] %(message)s'
    )
    
    logger = logging.getLogger()

    # Connect client to the running Temporal server
    client = await Client.connect("localhost:7233")

    # Run a worker for the workflow
    async with Worker(
        client,
        task_queue="hello-world-task-queue",
        workflows=[HelloWorldWorkflow],
        activities=[say_hello],
    ):
        # Worker runs until shut down
        logger.info(f"Worker-{worker_id} started. Ctrl+C to exit.")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main()) 