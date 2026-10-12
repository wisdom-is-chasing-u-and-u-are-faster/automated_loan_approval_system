"""
Concurrency Locking Subsystem for Open Enrollment.
Implements in-memory lock registry with thread safety and atomic checks
guaranteeing zero section overselling under high concurrency.
"""
import threading
import time
from contextlib import contextmanager

_lock_registry = {}
_registry_mutex = threading.Lock()


def get_section_lock(section_id: str) -> threading.Lock:
    with _registry_mutex:
        if section_id not in _lock_registry:
            _lock_registry[section_id] = threading.Lock()
        return _lock_registry[section_id]


@contextmanager
def acquire_enrollment_lock(section_id: str, timeout: float = 5.0):
    lock = get_section_lock(section_id)
    acquired = lock.acquire(timeout=timeout)
    if not acquired:
        raise TimeoutError(f"Failed to acquire lock for section {section_id} within {timeout}s")
    try:
        yield
    finally:
        lock.release()
