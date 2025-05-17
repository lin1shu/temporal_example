import asyncio
import logging
import random
import time
import sys

from temporalio.client import Client
from temporalio.exceptions import TemporalError, ServerError

from workflow import HelloWorldWorkflow

async def main():
    # Configure logging with more details
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    logger = logging.getLogger("starter")
    
    logger.info("Connecting to Temporal server...")
    try:
        # Connect client to the running Temporal server
        client = await Client.connect("localhost:7233")
        logger.info("Connected successfully to Temporal server")
    except Exception as e:
        logger.error(f"Failed to connect to Temporal server: {e}")
        return

    # Execute workflows continuously
    workflow_count = 0
    try:
        while True:
            # Generate a random number between 0 and 65535
            random_num = random.randint(0, 65535)
            name = f"World-{random_num}"
            
            workflow_count += 1
            logger.info(f"Starting workflow #{workflow_count} with parameter: {name}")
            
            try:
                # Execute workflow
                logger.info(f"Executing workflow with ID: hello-world-workflow-id-{random_num}")
                result = await client.execute_workflow(
                    HelloWorldWorkflow.run,
                    name,
                    id=f"hello-world-workflow-id-{random_num}",
                    task_queue="new-main-task-queue",
                )
                
                logger.info(f"Workflow completed with result: {result}")
            except ServerError as e:
                logger.error(f"Temporal server error: {e}")
            except TemporalError as e:
                logger.error(f"Temporal error: {e}")
            except Exception as e:
                logger.error(f"Error executing workflow: {e}")
            
            # Random delay between workflows (0 to 5 seconds)
            sleep_time = random.uniform(0, 5)
            logger.info(f"Sleeping for {sleep_time:.2f} seconds before next workflow...")
            await asyncio.sleep(sleep_time)
    except KeyboardInterrupt:
        logger.info("Workflow execution stopped by user")

if __name__ == "__main__":
    asyncio.run(main())
