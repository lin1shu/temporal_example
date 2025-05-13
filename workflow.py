from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import say_hello, say_hi

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
            task_queue="hello-world-task-queue",  # Explicit main task queue
        )
        
        # Call the say_hi activity with the result from say_hello on a dedicated task queue
        hi_result = await workflow.execute_activity(
            say_hi,
            hello_result,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
            task_queue="say-hi-task-queue",  # Special task queue for say_hi
        )
        
        return f"{hello_result} {hi_result}" 