import logging
import os
import re
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

@activity.defn
async def say_hi(hello_message: str) -> str:
    # Get hostname and process ID to identify the worker
    hostname = socket.gethostname()
    pid = os.getpid()
    
    # Extract all digits from the input string
    digits = re.findall(r'\d', hello_message)
    
    if digits:
        # Check if the last digit is even
        last_digit = int(digits[-1])
        if last_digit % 2 == 0:
            response = "hi"
        else:
            response = "what's up"
    else:
        # No digits found, default to "what's up"
        response = "what's up"
    
    # Log which worker is processing this activity
    logging.info(f"Activity say_hi processed by worker on {hostname} (PID: {pid})")
    
    return response 