# Temporal FAQ

## Basic Concepts

### Q: How does the starter and worker interaction work in Temporal?

**A:** The workers (launched by start_workers.py) only *poll* for tasks - they don't create any workflows themselves.

Workers connect to the Temporal server and essentially say "I'm available to do work on the 'new-main-task-queue' - do you have anything for me?"

If no one is submitting workflows (via starter.py), then the task queue remains empty.

The workers will continue polling indefinitely, but they won't execute anything because there are no tasks to process.

Only when you run starter.py does it actually create workflow executions and submit them to the task queue.

This separation of concerns is a fundamental design principle in Temporal:
- Workers are responsible for executing workflows and activities
- Clients (like starter.py) are responsible for initiating workflows

This design allows for independent scaling of both components. You can have many workers ready to handle high load, but they'll only activate when clients actually submit workflows to be executed.

### Q: Is "worker" a concept in Temporal?

**A:** Yes, "worker" is a core concept in Temporal. In the Temporal architecture:

A worker is a process that:
- Connects to the Temporal server
- Registers itself to handle specific workflows and activities
- Polls task queues for work to execute
- Runs the actual code for workflows and activities

Workers are central to Temporal's execution model because:

1. They host and execute your application code (workflows and activities)
2. They maintain local state for workflow executions
3. They communicate with the Temporal server to report progress and get new tasks
4. They handle task routing through task queues
5. They implement important features like activity retries and heartbeating

The separation between the Temporal server (which orchestrates and persists workflow state) and workers (which execute your code) is intentional. This allows your application code to run in your own environment with your specific dependencies, while Temporal handles the durability and coordination.

### Q: How do workers register with the Temporal server?

**A:** When workers connect to the Temporal server, they register themselves with specific information:

1. **Task Queue Name**: The worker declares which task queue(s) it will poll for work (in your example, "new-main-task-queue")

2. **Workflow Types**: The worker explicitly registers which workflow types it can execute (in your code, `workflows=[HelloWorldWorkflow]`)

3. **Activity Types**: The worker registers which activities it can execute (in your code, `activities=[say_hello]`)

This registration process tells the Temporal server:
- "I'm a worker that can handle HelloWorldWorkflow workflows"
- "I can execute the say_hello activity"
- "Send me tasks from the new-main-task-queue"

The Temporal server uses this information to route tasks appropriately. When a client submits a workflow execution request for "HelloWorldWorkflow" targeting the "new-main-task-queue", the server knows which workers can handle it.

This explicit registration is important because:
- It ensures tasks are only sent to workers that can handle them
- It allows for versioning and compatibility checks
- It enables targeted deployment (you can have different workers for different workflows)
- It supports the dynamic scaling of specific workflow types

## Activities and Workflows

### Q: Why does a worker have to declare which activities are supported? Are they part of the workflow defined?

**A:** Workers need to declare which activities they support for several important reasons:

1. **Decoupling of Workflow and Activity Execution**: 
   - In Temporal, workflows and activities can be executed by different workers
   - A workflow worker might schedule an activity, but a completely different activity worker could execute it

2. **Independent Scaling**:
   - You can have dedicated workers just for CPU-intensive activities
   - For example, you might have 5 workflow workers but 20 activity workers for compute-heavy tasks

3. **Targeted Deployment**:
   - Some activities might require special hardware (GPU) or environment configurations
   - By explicitly registering activities, you can run those specific activities only on appropriate machines

4. **Activity Versioning**:
   - Different versions of activities can coexist in the system
   - The registration helps Temporal route tasks to compatible workers

In your code, when a workflow calls an activity:

```python
# Inside HelloWorldWorkflow.run
result = await self.say_hello(name)
```

Temporal turns this into an activity task that's dispatched to a worker that has registered that activity. The worker that executes this activity might be the same one running the workflow, or it could be a completely different worker - Temporal handles all the routing.

So yes, activities are part of the workflow definition (the workflow code calls them), but their implementation and execution can be completely separate from the workflow itself. This separation is one of Temporal's powerful features for building distributed systems.

### Q: Can one worker execute a workflow, but its activities be executed on another worker? Aren't activities always part of a workflow?

**A:** Yes, activities are always part of a workflow conceptually - they're invoked by workflow code and their results are used within the workflow. However, the execution model in Temporal allows for distributed processing:

1. **Activities are part of workflows conceptually**:
   - Activities are always invoked from workflow code
   - The workflow depends on activity results
   - Logically, activities belong to workflows

2. **But physically, activities can execute separately**:
   - When a workflow calls an activity, Temporal creates an "activity task"
   - This task is placed on the specified task queue
   - Any worker polling that queue that has registered the activity can execute it
   - This might be the same worker running the workflow, or a completely different one

Here's what happens in sequence:

1. Worker A executes a workflow that calls `await self.say_hello(name)`
2. Temporal converts this to an activity task on the task queue
3. Worker B (which could be the same as A, or different) picks up the activity task
4. Worker B executes the activity and returns the result
5. Temporal delivers the result back to the workflow on Worker A
6. The workflow continues execution with the activity result

This separation provides several benefits:
- Activities can run on specialized hardware
- Activities can be scaled independently from workflows
- Activities can be retried separately from workflows
- Long-running activities don't block workflow execution

### Q: Can I register a workflow on one worker and its activities on a different worker on a different server?

**A:** Yes, that's exactly right! This is one of Temporal's powerful features for building distributed systems.

You can absolutely have:
- Worker-1 on Server A registering only workflow W1
- Worker-2 on Server B registering only activity A1
- Both workers polling the same task queue

When the workflow W1 runs on Worker-1 and calls activity A1:
1. Temporal creates an activity task and places it on the task queue
2. Worker-2 on Server B picks up this task since it registered A1
3. Worker-2 executes A1 and returns the result to Temporal
4. Temporal delivers the result back to the workflow W1 running on Worker-1

This distributed execution model allows for:
- Running activities on specialized hardware (like GPU servers for ML activities)
- Placing activities closer to resources they need (like database-intensive activities near the database)
- Independent scaling of workflow and activity processing
- Different resource allocations for workflows vs activities

You can implement this by:
1. Creating different worker processes with different registrations
2. Running these processes on different servers
3. Having them all connect to the same Temporal server
4. Using the same task queue name (or different queues with explicit routing)

This architecture gives you tremendous flexibility in how you distribute your workload across your infrastructure.

### Q: How does Temporal pass the parameters of an activity to a different worker? How does it serialize it?

**A:** Temporal handles parameter serialization between workers through a well-defined serialization process:

1. **Serialization Process**:
   - When a workflow calls an activity with parameters, Temporal serializes those parameters
   - By default, Temporal uses a protocol buffer (protobuf) based format called "Payload"
   - The serialized data is stored in the Temporal server's persistence layer
   - When an activity worker polls for tasks, it receives these serialized parameters

2. **Data Types Support**:
   - Temporal can serialize primitive types (strings, numbers, booleans)
   - It also handles complex data structures (lists, dictionaries/maps)
   - Custom objects are serialized based on the SDK's conventions
   - In Python, the temporalio SDK uses JSON serialization by default

3. **Custom Serialization**:
   - Temporal allows for custom data converters if you need special serialization
   - This is useful for binary data, encrypted data, or custom formats
   - You can register custom converters with the client/worker

For example, in your Python code:

```python
@activity.defn
async def say_hello(name: str) -> str:
    # 'name' was serialized by the workflow worker,
    # transmitted through Temporal server,
    # and deserialized here by the activity worker
    return f"Hello, {name}!"
```

The parameter `name` is:
1. Serialized to JSON by the workflow worker
2. Stored in Temporal's persistence
3. Retrieved by the activity worker
4. Deserialized from JSON back to a Python string

This serialization/deserialization is handled automatically by the Temporal SDK, making it transparent to your code. It allows activities and workflows to run on completely different processes or machines while still communicating effectively.

## Parallel Execution and DAG Workflows

### Q: How does Temporal handle parallel activity execution?

**A:** Temporal's approach to parallel activity execution is fundamentally different from traditional multi-threading or multiprocessing:

1. **Workflow Determinism**:
   - Workflow code is always single-threaded and deterministic
   - Even when dealing with parallel activities, the workflow itself runs sequentially

2. **Distributed Activity Execution**:
   - When a workflow needs to run activities in parallel, it schedules all of them with the Temporal server
   - The server dispatches these activities as separate tasks
   - Different workers can pick up these tasks and execute them simultaneously
   - The parallelism comes from having multiple workers, not from multithreading in the workflow code

3. **Task Queues as Coordination Mechanism**:
   - Activity tasks are placed on task queues
   - Multiple workers can poll the same queue or dedicated queues
   - Temporal handles the coordination and routing of tasks to available workers

4. **Waiting for Parallel Completion**:
   - The workflow can use `await asyncio.gather()` (Python) to wait for multiple activities
   - This doesn't block the worker thread - Temporal will pause the workflow execution
   - When all activities complete, Temporal resumes the workflow with all results

For example, in our DAG workflow:

```python
# Schedule three activities in parallel
a_task = workflow.execute_activity(activity_a, ...)
b_task = workflow.execute_activity(activity_b, ...)
c_task = workflow.execute_activity(activity_c, ...)

# Wait for all to complete
a_result, b_result, c_result = await asyncio.gather(a_task, b_task, c_task)

# Proceed with results from all three
d_result = await workflow.execute_activity(activity_d, args=[a_result, b_result, c_result], ...)
```

This pattern allows for true parallelism without sacrificing workflow determinism.

### Q: Are parallel activities executed in threads or separate processes?

**A:** Parallel activities in Temporal are typically executed in separate processes, not threads:

1. **Default Execution Model**:
   - By default, a single worker process handles one activity at a time sequentially
   - Parallelism comes from having multiple worker processes

2. **Worker Process Independence**:
   - Each worker process runs independently
   - Separate worker processes can execute different activities simultaneously
   - Activities in different processes are truly parallel (not constrained by Python's GIL)

3. **Configurable Worker Concurrency**:
   - Workers can be configured with `max_concurrent_activities` to process multiple activities
   - Even with concurrent processing, each activity gets its own isolated execution context

4. **Dedicated Workers for Specific Activities**:
   - As demonstrated in our implementation, you can create dedicated workers for specific activities
   - Worker-1 for Activity A, Worker-2 for Activity B, etc.
   - Using dedicated task queues guarantees activities run on their assigned workers

In our DAG example, we specifically designed the system so:
- Each parallel activity (A, B, C) has its own dedicated task queue
- Each activity is registered on a specific worker (1, 2, or 3)
- The logs show different PIDs for each activity, confirming they run in separate processes
- This ensures true parallelism even when all workers run on the same machine

### Q: If all parallel activities A, B, and C are picked up by the same worker, will they still run in parallel?

**A:** If all parallel activities A, B, and C are picked up by the same worker process with default settings, they will be executed sequentially, not in parallel:

1. **Default Worker Behavior**:
   - By default, a Temporal worker processes one activity at a time
   - Even though the workflow code schedules them "in parallel" with `asyncio.gather()`, the execution happens one after another if there's only one worker

2. **Options for True Parallelism**:
   - **Multiple Worker Processes**: Run multiple worker processes (most reliable approach)
   - **Worker Concurrency Settings**: Configure the worker with `max_concurrent_activities` parameter
   - **Dedicated Task Queues**: Assign activities to different task queues handled by different workers

3. **Our Implementation Approach**:
   - We use dedicated task queues (e.g., "new-activity-a-task-queue", "new-activity-b-task-queue", "new-activity-c-task-queue", "new-say-hi-task-queue")
   - We configure specific workers to handle specific task queues 
   - This guarantees activities run on separate worker processes, ensuring true parallelism

The logs from our implementation clearly show this pattern:
```
[Worker-1] Activity A processed by worker on yishul-mlt (PID: 91027)
[Worker-2] Activity B processed by worker on yishul-mlt (PID: 91029)
[Worker-3] Activity C processed by worker on yishul-mlt (PID: 91030)
```

Different PIDs confirm the activities are running in separate processes, achieving true parallelism.

### Q: How does Temporal implement DAGs (Directed Acyclic Graphs) of activities?

**A:** Temporal doesn't have an explicit "DAG" construct, but it enables DAG patterns through its workflow programming model:

1. **Workflow Code as the DAG Definition**:
   - The workflow code itself defines the DAG structure
   - Sequential dependencies are expressed through `await` statements
   - Parallel execution is achieved by scheduling multiple activities and waiting for all

2. **Activity Dependencies**:
   - Activities can depend on the results of other activities
   - The workflow code enforces these dependencies
   - Temporal ensures the correct execution order

3. **Example DAG Implementation**:
   ```python
   # Sequential dependency
   hello_result = await workflow.execute_activity(say_hello, name, ...)
   hi_result = await workflow.execute_activity(say_hi, hello_result, ...)
   
   # Parallel activities (fan-out)
   a_task = workflow.execute_activity(activity_a, ...)
   b_task = workflow.execute_activity(activity_b, ...)
   c_task = workflow.execute_activity(activity_c, ...)
   
   # Join point (fan-in)
   a_result, b_result, c_result = await asyncio.gather(a_task, b_task, c_task)
   
   # Final activity depends on all parallel results
   d_result = await workflow.execute_activity(activity_d, args=[a_result, b_result, c_result], ...)
   ```

4. **Benefits of This Approach**:
   - The DAG is expressed as normal code, making it intuitive
   - Dependencies are type-checked by the language
   - Data flows naturally between activities
   - The workflow can include conditional logic and dynamic DAG structures

This model allows for complex DAG structures while maintaining workflow determinism and the ability to replay history correctly after failures.

## Workflow Resumption and Replay Mechanism

### Q: Where are workflows actually executed? On the worker or Temporal's server?

**A:** Workflows are executed on the worker, not on Temporal's server. However, this is more nuanced than it appears:

1. **Workflow Code Location**: 
   - Your actual workflow code runs on the worker process
   - All your business logic executes in your environment, not on Temporal's servers

2. **Workflow State Management**:
   - While the code runs on the worker, all workflow decisions and state changes are recorded and sent to Temporal server
   - Temporal server stores this execution history as the source of truth
   - The history becomes the persistent, durable record of the workflow

3. **What Happens During "Waiting"**:
   - When a workflow reaches `await asyncio.gather()` for parallel activities, the worker doesn't actually block
   - Instead, the worker records a "waiting state" in the workflow history
   - The workflow task completes and the worker returns control to Temporal
   - The workflow execution is effectively paused on the worker side

4. **Example in Logs**:
   Our logs show this clearly:
   ```
   # Workflow execution is distributed across different workers
   [Worker-6] Activity for World-46049 processed by worker on yishul-mlt (PID: 98645)
   [Worker-5] Activity say_hi processed by worker on yishul-mlt (PID: 98644)
   [Worker-1] Activity A processed by worker on yishul-mlt (PID: 98635)
   [Worker-2] Activity B processed by worker on yishul-mlt (PID: 98636)
   [Worker-3] Activity C processed by worker on yishul-mlt (PID: 98640)
   [Worker-7] Activity D processed by worker on yishul-mlt (PID: 98646)
   ```

### Q: Can a paused workflow be resumed on another worker?

**A:** Yes, a paused workflow can be resumed on an entirely different worker than the one where it was initially running. This is a core feature of Temporal's architecture:

1. **History-Based State Transfer**:
   - The complete workflow execution history is stored on the Temporal server
   - When activities complete, any available worker can pick up the workflow task
   - This worker might be different from the one that started the workflow

2. **Workflow Replay Mechanism**:
   - The new worker receives the complete execution history
   - It replays the workflow code from the beginning using the history
   - It skips re-executing completed activities and instead uses their recorded results
   - This continues until it reaches the current execution point

3. **Real Example from Our Logs**:
   Looking at our logs, we can see this happening in practice:
   ```
   # First workflow executes say_hello on Worker-9, but activity_d on Worker-5
   [Worker-9] Activity for World-54214 processed by worker on yishul-mlt (PID: 98648)
   [Worker-5] Activity say_hi processed by worker on yishul-mlt (PID: 98644)
   [Worker-1] Activity A processed by worker on yishul-mlt (PID: 98635)
   [Worker-2] Activity B processed by worker on yishul-mlt (PID: 98636)
   [Worker-3] Activity C processed by worker on yishul-mlt (PID: 98640)
   [Worker-5] Activity D processed by worker on yishul-mlt (PID: 98644)
   
   # Next workflow uses different workers for each stage
   [Worker-7] Activity for World-12999 processed by worker on yishul-mlt (PID: 98646)
   [Worker-5] Activity say_hi processed by worker on yishul-mlt (PID: 98644)
   [Worker-1] Activity A processed by worker on yishul-mlt (PID: 98635)
   [Worker-3] Activity C processed by worker on yishul-mlt (PID: 98640)
   [Worker-2] Activity B processed by worker on yishul-mlt (PID: 98636)
   [Worker-4] Activity D processed by worker on yishul-mlt (PID: 98641)
   ```

### Q: How does workflow resumption work with custom code/logic?

**A:** Temporal's ability to resume workflows on different workers with custom code relies on several key principles:

1. **Event Sourcing Architecture**:
   - Every workflow action is recorded as an event in the history
   - This history is the source of truth, not any in-memory state
   - The history includes all inputs, outputs, and decision points

2. **Deterministic Replay**:
   - When a worker picks up a workflow, it receives the complete history
   - The worker executes the workflow code from the beginning
   - For completed activities, it uses results from history instead of re-executing
   - The code must produce the same decisions given the same inputs

3. **Custom Logic Handling**:
   - All your custom workflow logic executes on the worker
   - But it must be deterministic - given the same inputs, it must make the same decisions
   - Non-deterministic operations (random numbers, current time) use special APIs

4. **Replay to Current Point**:
   - The worker doesn't "jump" to the paused point
   - It replays the entire workflow code extremely quickly because:
     - Activities aren't actually re-executed during replay
     - Results from history are used instead
     - Custom logic is re-executed, but deterministically

5. **Example from Our Implementation**:
   In our code, a workflow might start on Worker-9, then when it needs to wait for activities, it completes that task. Later, when the activities complete, Worker-4 might pick up the workflow:
   ```python
   # Initially executed on Worker-9
   hello_result = await workflow.execute_activity(say_hello, name) # Executed on Worker-6
   hi_result = await workflow.execute_activity(say_hi, hello_result) # Executed on Worker-5
   
   # Worker-9 task completes here, waiting for activities
   # When activities complete, Worker-4 picks up the workflow and replays to this point
   
   # Worker-4 now continues execution
   a_task = workflow.execute_activity(activity_a)
   b_task = workflow.execute_activity(activity_b)
   c_task = workflow.execute_activity(activity_c)
   
   # Worker-4 task completes here, waiting for parallel activities
   # When A, B, C complete, maybe Worker-8 picks up the workflow
   a_result, b_result, c_result = await asyncio.gather(a_task, b_task, c_task)
   
   # Worker-8 continues execution
   d_result = await workflow.execute_activity(activity_d, args=[a_result, b_result, c_result])
   ```

The logs confirm this distributed execution pattern across multiple workers, with each picking up where the previous left off, thanks to the deterministic replay mechanism.
