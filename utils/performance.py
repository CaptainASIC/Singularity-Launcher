"""
Performance monitoring utilities for Singularity Launcher
Provides caching and optimization for performance-intensive operations.

Version 2.5.0 - Enhanced UI & Optimized Scripts
"""
import streamlit as st
import time
import functools
import logging
from typing import Any, Callable, Dict, List, Optional, Union, Tuple
import threading
import queue

logger = logging.getLogger("singularity_launcher")

# Cache for performance-intensive operations
_function_cache = {}
_cache_expiry = {}

def cached_operation(ttl_seconds: int = 60):
    """
    Decorator for caching performance-intensive operations.
    
    Args:
        ttl_seconds: Time to live for cached results in seconds
        
    Returns:
        Decorated function with caching
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check if result is in cache and not expired
            current_time = time.time()
            if cache_key in _function_cache and current_time < _cache_expiry.get(cache_key, 0):
                logger.debug(f"Cache hit for {func.__name__}")
                return _function_cache[cache_key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            _function_cache[cache_key] = result
            _cache_expiry[cache_key] = current_time + ttl_seconds
            
            logger.debug(f"Cache miss for {func.__name__}, cached for {ttl_seconds}s")
            return result
        return wrapper
    return decorator

def clear_cache():
    """
    Clear all cached results.
    """
    global _function_cache, _cache_expiry
    _function_cache = {}
    _cache_expiry = {}
    logger.info("Cache cleared")

class AsyncTaskManager:
    """
    Manages asynchronous tasks for improved UI responsiveness.
    """
    _tasks = {}
    _results = {}
    _task_queue = queue.Queue()
    _worker_thread = None
    _is_running = False
    
    @classmethod
    def initialize(cls):
        """
        Initialize the async task manager.
        """
        if cls._worker_thread is None or not cls._worker_thread.is_alive():
            cls._is_running = True
            cls._worker_thread = threading.Thread(target=cls._worker_loop, daemon=True)
            cls._worker_thread.start()
            logger.info("AsyncTaskManager initialized")
    
    @classmethod
    def _worker_loop(cls):
        """
        Worker loop for processing async tasks.
        """
        while cls._is_running:
            try:
                # Get task from queue with timeout
                task_id, func, args, kwargs = cls._task_queue.get(timeout=1)
                
                # Execute task
                try:
                    result = func(*args, **kwargs)
                    cls._results[task_id] = {"status": "completed", "result": result}
                except Exception as e:
                    logger.error(f"Error in async task {task_id}: {str(e)}")
                    cls._results[task_id] = {"status": "error", "error": str(e)}
                
                # Mark task as done
                cls._task_queue.task_done()
                
            except queue.Empty:
                # No tasks in queue, continue loop
                pass
            except Exception as e:
                logger.error(f"Error in worker loop: {str(e)}")
                time.sleep(1)  # Prevent CPU spinning on repeated errors
    
    @classmethod
    def submit_task(cls, func: Callable, *args, **kwargs) -> str:
        """
        Submit a task for asynchronous execution.
        
        Args:
            func: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Task ID for checking results
        """
        # Ensure worker is running
        cls.initialize()
        
        # Generate task ID
        task_id = f"task_{time.time()}_{id(func)}"
        
        # Add task to queue
        cls._tasks[task_id] = {"func": func.__name__, "submitted": time.time()}
        cls._results[task_id] = {"status": "pending"}
        cls._task_queue.put((task_id, func, args, kwargs))
        
        logger.debug(f"Submitted async task {task_id}")
        return task_id
    
    @classmethod
    def get_task_result(cls, task_id: str) -> Dict[str, Any]:
        """
        Get the result of an async task.
        
        Args:
            task_id: Task ID to check
            
        Returns:
            Task result dictionary with status and result/error
        """
        if task_id not in cls._results:
            return {"status": "unknown"}
        
        return cls._results[task_id]
    
    @classmethod
    def cleanup_old_tasks(cls, max_age_seconds: int = 3600):
        """
        Clean up old task results to prevent memory leaks.
        
        Args:
            max_age_seconds: Maximum age of task results to keep
        """
        current_time = time.time()
        task_ids_to_remove = []
        
        for task_id, task_info in cls._tasks.items():
            if current_time - task_info["submitted"] > max_age_seconds:
                task_ids_to_remove.append(task_id)
        
        for task_id in task_ids_to_remove:
            if task_id in cls._tasks:
                del cls._tasks[task_id]
            if task_id in cls._results:
                del cls._results[task_id]
        
        logger.debug(f"Cleaned up {len(task_ids_to_remove)} old tasks")
    
    @classmethod
    def shutdown(cls):
        """
        Shutdown the async task manager.
        """
        cls._is_running = False
        if cls._worker_thread and cls._worker_thread.is_alive():
            cls._worker_thread.join(timeout=2)
        logger.info("AsyncTaskManager shutdown")

# Initialize AsyncTaskManager when module is imported
AsyncTaskManager.initialize()

def measure_execution_time(func):
    """
    Decorator to measure execution time of functions.
    
    Args:
        func: Function to measure
        
    Returns:
        Decorated function with timing
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
        return result
    return wrapper
