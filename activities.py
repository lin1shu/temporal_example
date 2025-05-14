import logging
import os
import re
import socket
import random
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

@activity.defn
async def activity_a() -> str:
    hostname = socket.gethostname()
    pid = os.getpid()
    
    # Generate random number for A
    random_num = random.randint(1000, 9999)
    message = f"A: {random_num}"
    
    logging.info(f"Activity A processed by worker on {hostname} (PID: {pid})")
    logging.info(f"A generated: {random_num}")
    
    return message

@activity.defn
async def activity_b() -> str:
    hostname = socket.gethostname()
    pid = os.getpid()
    
    # Generate random number for B
    random_num = random.randint(1000, 9999)
    message = f"B: {random_num}"
    
    logging.info(f"Activity B processed by worker on {hostname} (PID: {pid})")
    logging.info(f"B generated: {random_num}")
    
    return message

@activity.defn
async def activity_c() -> str:
    hostname = socket.gethostname()
    pid = os.getpid()
    
    # Generate random number for C
    random_num = random.randint(1000, 9999)
    message = f"C: {random_num}"
    
    logging.info(f"Activity C processed by worker on {hostname} (PID: {pid})")
    logging.info(f"C generated: {random_num}")
    
    return message

@activity.defn
async def activity_d(*args) -> str:
    """
    Compatibility wrapper that handles both:
    - New format: activity_d([a_result, b_result, c_result])
    - Old format: activity_d(a_result, b_result, c_result)
    """
    hostname = socket.gethostname()
    pid = os.getpid()
    
    # Handle both parameter formats
    if len(args) == 1 and isinstance(args[0], list):
        # New format: single list argument
        results = args[0]
        a_result = results[0]
        b_result = results[1]
        c_result = results[2]
        logging.info(f"Activity D received results in new format (list)")
    elif len(args) == 3:
        # Old format: three separate arguments
        a_result, b_result, c_result = args
        logging.info(f"Activity D received results in old format (separate args)")
    else:
        # Unknown format
        logging.error(f"Activity D received unknown argument format: {args}")
        return f"Error: Unknown argument format"
    
    # Extract the numbers from the activity results
    a_num = a_result.split(": ")[1] if ": " in a_result else "unknown"
    b_num = b_result.split(": ")[1] if ": " in b_result else "unknown"
    c_num = c_result.split(": ")[1] if ": " in c_result else "unknown"
    
    message = f"D received: {a_num} from A, {b_num} from B, {c_num} from C"
    
    logging.info(f"Activity D processed by worker on {hostname} (PID: {pid})")
    logging.info(f"D received results: {a_result}, {b_result}, {c_result}")
    
    return message 