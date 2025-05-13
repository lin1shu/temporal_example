import logging
import os
import socket
from temporalio import activity

@activity.defn
async def say_hello(name: str) -> str:
    # Get hostname and process ID to identify the worker
    hostname = socket.gethostname()
    pid = os.getpid()
    
    message = f"Hello, {name}!"
    
    # Log which worker is processing this activity
    logging.info(f"Activity for {name} processed by worker on {hostname} (PID: {pid})")
    
    return message 