import pytest
import time
from bot.cache import CacheFor

def create_counted_func():
    call_count = 0

    def counted_func(a, b):
        nonlocal call_count
        call_count += 1
        return (a + b, call_count)

    return counted_func

counted_func = create_counted_func()
cached_counted_func = CacheFor(duration=2, enable_logging=True)(counted_func)

@pytest.fixture
def time_travel():
    original_time = time.time

    def shift_time(seconds):
        class TimeShift:
            def __init__(self, shift):
                self.shift = shift

            def __call__(self):
                return original_time() + self.shift
        time.time = TimeShift(seconds)

    yield shift_time

    time.time = original_time

def test_cached_counted_func_behavior(time_travel):
    # Call the decorated function for the first time
    result1, call_count1 = cached_counted_func(1, 2)
    assert call_count1 == 1  # Function should have been called once

    # Call again with the same arguments to hit the cache
    result2, call_count2 = cached_counted_func(1, 2)
    assert call_count2 == call_count1  # Call count should not increase

    # Simulate cache expiration
    time_travel(2.1)

    # Call the function again after cache expiration
    result3, call_count3 = cached_counted_func(1, 2)
    assert call_count3 == call_count1 + 1  # Call count should increase by 1, indicating a re-execution
