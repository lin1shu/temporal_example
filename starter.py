import asyncio
import logging
import random
import time

from temporalio.client import Client

from workflow import HelloWorldWorkflow

async def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Connect client to the running Temporal server
    client = await Client.connect("localhost:7233")

    # Execute workflows continuously
    workflow_count = 0
    try:
        while True:
            # Generate a random number between 0 and 65535
            random_num = random.randint(0, 65535)
            name = f"World-{random_num}"
            
            workflow_count += 1
            print(f"Starting workflow #{workflow_count} with parameter: {name}")
            
            # Execute workflow
            result = await client.execute_workflow(
                HelloWorldWorkflow.run,
                name,
                id=f"hello-world-workflow-id-{random_num}",
                task_queue="hello-world-task-queue",
            )
            
            print(f"Workflow result: {result}")
            
            # Random delay between workflows (0 to 5 seconds)
            sleep_time = random.uniform(0, 5)
            print(f"Sleeping for {sleep_time:.2f} seconds before next workflow...")
            await asyncio.sleep(sleep_time)
    except KeyboardInterrupt:
        print("Workflow execution stopped by user")

if __name__ == "__main__":
    asyncio.run(main()) 