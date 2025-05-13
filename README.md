# Temporal Hello World Example

This is a simple Temporal application that demonstrates a basic workflow and activity.

## Prerequisites

- Python 3.7 or later
- Temporal server running locally (see [Temporal Server Setup](TEMPORAL_SERVER.md))

## Installation

```bash
pip3 install temporalio
```

## Running the Application

1. Start the Temporal server:
   ```bash
   cd /Users/yishu/code/temporal-server
   docker-compose up -d
   ```

2. In one terminal, start the worker:
   ```bash
   python3 worker.py
   ```
   The worker will connect to the Temporal server and wait for tasks. Keep this terminal running.

3. In another terminal, run the workflow:
   ```bash
   python3 starter.py
   ```
   You should see output like:
   ```
   Starting workflow with parameter: World
   Workflow result: Hello, World!
   ```

4. You can view the workflow execution in the Temporal Web UI:
   ```
   http://localhost:8080
   ```

## How It Works

1. **Components**:
   - **Temporal Server**: Orchestration engine that manages workflows
   - **Worker**: Process that polls for and executes workflow and activity tasks
   - **Workflow**: Business logic defining the sequence of operations
   - **Activities**: Individual units of work that can be retried independently

2. **Execution Flow**:
   - The worker connects to Temporal and registers for the "hello-world-task-queue"
   - The starter initiates a workflow with the parameter "World"
   - Temporal dispatches the workflow task to our worker
   - The workflow executes and calls the "say_hello" activity
   - The activity runs, printing and returning "Hello, World!"
   - The result is returned to the workflow and then to the starter

3. **Key Benefits**:
   - **Durability**: Workflow state persists through crashes
   - **Retries**: Activities automatically retry on failure
   - **Visibility**: Monitor executions in the Temporal UI
   - **Scalability**: Multiple workers can process tasks concurrently

## Project Structure

- `workflow.py`: Contains the HelloWorldWorkflow definition
- `activities.py`: Contains the say_hello activity
- `worker.py`: Registers and runs the workflow and activities
- `starter.py`: Initiates the workflow execution
- `TEMPORAL_SERVER.md`: Instructions for setting up and running the Temporal server 