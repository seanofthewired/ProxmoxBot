'''
Proxmox VM Manager Bot: A Discord bot for managing Proxmox virtual machines.
Copyright (C) 2024  Brian J. Royer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact me at: brian.royer@gmail.com or https://github.com/shyce
'''

import functools
import time
import logging

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
                    logging.info(f"Cache hit for {func.__name__}{args}{kwargs.items()}")
                    return result
                else:
                    logging.info(f"Cache expired for {func.__name__}{args}{kwargs.items()}")

            # If not in cache or expired, compute the result and cache it
            result = func(*args, **kwargs)
            cached_results[key] = (result, current_time)
            logging.info(f"Result cached for {func.__name__}{args}{kwargs.items()}")
            return result

        return wrapper

    return decorator
