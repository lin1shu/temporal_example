import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from activities import say_hello
from workflow import HelloWorldWorkflow

async def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)

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
        print("Worker started. Ctrl+C to exit.")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main()) 