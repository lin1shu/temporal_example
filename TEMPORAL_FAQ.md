# Temporal FAQ

## Basic Concepts

### Q: How does the starter and worker interaction work in Temporal?

**A:** The workers (launched by start_workers.py) only *poll* for tasks - they don't create any workflows themselves.

Workers connect to the Temporal server and essentially say "I'm available to do work on the 'hello-world-task-queue' - do you have anything for me?"

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

1. **Task Queue Name**: The worker declares which task queue(s) it will poll for work (in your example, "hello-world-task-queue")

2. **Workflow Types**: The worker explicitly registers which workflow types it can execute (in your code, `workflows=[HelloWorldWorkflow]`)

3. **Activity Types**: The worker registers which activities it can execute (in your code, `activities=[say_hello]`)

This registration process tells the Temporal server:
- "I'm a worker that can handle HelloWorldWorkflow workflows"
- "I can execute the say_hello activity"
- "Send me tasks from the hello-world-task-queue"

The Temporal server uses this information to route tasks appropriately. When a client submits a workflow execution request for "HelloWorldWorkflow" targeting the "hello-world-task-queue", the server knows which workers can handle it.

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