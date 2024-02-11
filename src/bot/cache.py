import functools
import logging
import time


def cache_for(duration):
    def decorator(func):
        cached_results = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            key = (func.__name__, args, tuple(kwargs.items()))

            # Check if the result is in the cache and not expired
            if key in cached_results:
                result, timestamp = cached_results[key]
                if current_time - timestamp < duration:
                    logging.info(f"Cache hit for {func.__name__}{
                                 args}{kwargs.items()}")
                    return result
                else:
                    logging.info(
                        f"Cache expired for {func.__name__}{
                            args}{kwargs.items()}"
                    )

            # If not in cache or expired, compute the result and cache it
            result = func(*args, **kwargs)
            cached_results[key] = (result, current_time)
            logging.info(f"Result cached for {func.__name__}{
                         args}{kwargs.items()}")
            return result

        return wrapper

    return decorator
