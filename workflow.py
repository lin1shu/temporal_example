from datetime import timedelta
import asyncio
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import say_hello, say_hi, activity_a, activity_b, activity_c, activity_d

@workflow.defn
class HelloWorldWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        # Call the say_hello activity with a retry policy
        hello_result = await workflow.execute_activity(
            say_hello,
            name,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
            task_queue="new-main-task-queue",  # New task queue name
        )
        
        # Call the say_hi activity with the result from say_hello on a dedicated task queue
        hi_result = await workflow.execute_activity(
            say_hi,
            hello_result,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
            task_queue="new-say-hi-task-queue",  # New task queue name
        )
        
        # Execute activities A, B, and C in parallel on dedicated workers
        a_task = workflow.execute_activity(
            activity_a,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
            task_queue="new-activity-a-task-queue",  # New task queue name
        )
        
        b_task = workflow.execute_activity(
            activity_b,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
            task_queue="new-activity-b-task-queue",  # New task queue name
        )
        
        c_task = workflow.execute_activity(
            activity_c,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
            task_queue="new-activity-c-task-queue",  # New task queue name
        )
        
        # Wait for all parallel tasks to complete
        a_result, b_result, c_result = await asyncio.gather(a_task, b_task, c_task)
        
        # Execute activity D after A, B, and C are complete
        # Pass the results as a single list argument rather than multiple positional args
        d_result = await workflow.execute_activity(
            activity_d,
            args=[a_result, b_result, c_result],  # Pass as args list
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
            task_queue="new-main-task-queue",  # New task queue name
        )
        
        # Format the final result to show the DAG execution
        workflow_result = (
            f"Sequential: {hello_result} -> {hi_result}\n"
            f"Parallel: [{a_result}, {b_result}, {c_result}]\n"
            f"Final: {d_result}"
        )
        
        return workflow_result
