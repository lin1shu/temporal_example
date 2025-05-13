from temporalio import activity

@activity.defn
async def say_hello(name: str) -> str:
    message = f"Hello, {name}!"
    print(message)  # This will print in the worker's console
    return message 