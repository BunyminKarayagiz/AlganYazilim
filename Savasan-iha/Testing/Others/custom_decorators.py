import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def perf_counter(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()  # Start the timer
        result = func(*args, **kwargs)  # Call the function
        end = time.perf_counter()  # End the timer
        print(f"Execution time of {func.__name__}: {end - start} seconds")
        return result  # Return the result of the function
    return wrapper

def debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {func.__name__} with args: {args} and kwargs: {kwargs}")  # Log the function call details
        result = func(*args, **kwargs)  # Call the function
        logger.debug(f"{func.__name__} returned: {result}")  # Log the return value
        return result  # Return the result of the function
    return wrapper

#? Aşırı yönelim için kullanılabilir.
def memoize(func):
    cache = {}
    @wraps(func)
    def wrapper(*args):
        if args in cache:
            return cache[args]
        else:
            result = func(*args)
            cache[args] = result
            return result
    return wrapper