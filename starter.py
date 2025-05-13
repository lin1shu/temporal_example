import asyncio
import logging

from temporalio.client import Client

from workflow import HelloWorldWorkflow

async def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Connect client to the running Temporal server
    client = await Client.connect("localhost:7233")

    # Execute a workflow
    name = "World"
    print(f"Starting workflow with parameter: {name}")
    
    result = await client.execute_workflow(
        HelloWorldWorkflow.run,
        name,
        id="hello-world-workflow-id",
        task_queue="hello-world-task-queue",
    )
    
    print(f"Workflow result: {result}")

if __name__ == "__main__":
    asyncio.run(main()) 