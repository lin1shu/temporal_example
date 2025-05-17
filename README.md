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

### Basic Setup

1. Start the Temporal server:
   ```bash
   cd /Users/yishul/code/temporal-server
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

### Advanced Setup with Multiple Workers

This application supports running multiple workers in parallel for increased throughput and to demonstrate a distributed system.

1. Start 10 worker processes in parallel:
   ```bash
   python3 start_workers.py
   ```
   This will start 10 worker processes, each with a unique ID. The script will automatically restart any worker that crashes.

2. In another terminal, run the continuous workflow starter:
   ```bash
   python3 starter.py
   ```
   This will continuously submit workflows with random names ("World-XXXXX") and random delays between submissions.

3. To stop the processes:
   ```bash
   # Stop the starter
   pkill -f "python3 starter.py"

   # Stop all workers (including the start_workers.py script)
   pkill -f "python3 start_workers.py"
   pkill -f "python3 worker.py"
   ```

## How It Works

1. **Components**:
   - **Temporal Server**: Orchestration engine that manages workflows
   - **Worker**: Process that polls for and executes workflow and activity tasks
   - **Workflow**: Business logic defining the sequence of operations
   - **Activities**: Individual units of work that can be retried independently

2. **Execution Flow**:
   - The worker connects to Temporal and registers for the "new-main-task-queue"
   - The starter initiates a workflow with the parameter "World"
   - Temporal dispatches the workflow task to our worker
   - The workflow executes and calls the "say_hello" activity
   - The activity runs, printing and returning "Hello, World!"
   - The result is returned to the workflow and then to the starter

3. **Multi-Worker Parallelism**:
   - Multiple workers connect to the same task queue
   - Workers compete to execute workflows (first available worker gets the task)
   - Each worker runs independently and can process workflows in parallel
   - The system demonstrates horizontal scaling capabilities

4. **Key Benefits**:
   - **Durability**: Workflow state persists through crashes
   - **Retries**: Activities automatically retry on failure
   - **Visibility**: Monitor executions in the Temporal UI
   - **Scalability**: Multiple workers can process tasks concurrently

## DAG Workflow Implementation

This project includes a Directed Acyclic Graph (DAG) workflow that demonstrates how to implement parallel activity execution in Temporal:

1. **DAG Structure**:
   - Sequential execution: `say_hello` → `say_hi`
   - Parallel execution: Activities A, B, and C run concurrently
   - Final execution: Activity D runs after all parallel activities complete

2. **Dedicated Worker Assignment**:
   - Activity A runs exclusively on Worker-1 via the `new-activity-a-task-queue`
   - Activity B runs exclusively on Worker-2 via the `new-activity-b-task-queue`
   - Activity C runs exclusively on Worker-3 via the `new-activity-c-task-queue`
   - Activity `say_hi` runs exclusively on Worker-5 via the `new-say-hi-task-queue`
   - All workers can handle `say_hello` and Activity D on the `new-main-task-queue`

3. **Data Flow**:
   - Each parallel activity (A, B, C) generates a random number
   - Activity D receives results from all three parallel activities
   - This demonstrates how Temporal coordinates data dependencies in a DAG

4. **Visualization**:
   ```
   [say_hello] → [say_hi] → [A, B, C] → [D]
                             ↓  ↓  ↓
                             All results
                             combined in D
   ```

5. **True Parallelism**:
   - By assigning activities to dedicated task queues (e.g., `new-say-hi-task-queue`, `new-activity-a-task-queue`, etc.), we ensure true parallel execution
   - Even when running on a single machine, activities execute on separate worker processes
   - The logs clearly show different PIDs for each parallel activity execution

## Project Structure

- `workflow.py`: Contains the HelloWorldWorkflow definition with DAG implementation
- `activities.py`: Contains all activity definitions (say_hello, say_hi, A, B, C, D)
- `worker.py`: Registers and runs the workflow and activities on dedicated workers
- `starter.py`: Initiates the workflow execution continuously with random names
- `start_workers.py`: Script to start and manage multiple worker processes
- `TEMPORAL_SERVER.md`: Instructions for setting up and running the Temporal server
- `TEMPORAL_FAQ.md`: Frequently asked questions about Temporal concepts
