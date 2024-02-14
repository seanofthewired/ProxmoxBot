import functools
import logging
import time

class CacheFor:
    def __init__(self, duration, enable_logging=True):
        self.duration = duration
        self.cache = {}
        self.enable_logging = enable_logging

    def log(self, message):
        if self.enable_logging:
            logging.basicConfig(level=logging.INFO)
            logging.info(message)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            key = (func.__name__, args, tuple(kwargs.items()))
            if key in self.cache:
                result, timestamp = self.cache[key]
                if current_time - timestamp < self.duration:
                    self.log(f"Cache hit for {func.__name__}{args}{kwargs}")
                    return result
                else:
                    self.log(f"Cache expired for {func.__name__}{args}{kwargs}")
            
            result = func(*args, **kwargs)
            self.cache[key] = (result, current_time)
            self.log(f"Result cached for {func.__name__}{args}{kwargs}")
            return result

        return wrapper
