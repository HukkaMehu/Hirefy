"""Verification task manager for parallel verification execution."""

import logging
import threading
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from enum import Enum

from src.database.models import db, VerificationSession, Employment

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of a verification task"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class VerificationTask:
    """Represents a single verification task"""
    
    def __init__(
        self,
        task_id: str,
        task_type: str,
        target_id: str,
        execute_fn: Callable,
        execute_args: Dict[str, Any]
    ):
        self.task_id = task_id
        self.task_type = task_type  # 'EMPLOYMENT', 'REFERENCE', 'EDUCATION', 'TECHNICAL'
        self.target_id = target_id  # ID of the record being verified
        self.execute_fn = execute_fn
        self.execute_args = execute_args
        self.status = TaskStatus.PENDING
        self.result = None
        self.error_message = None
        self.started_at = None
        self.completed_at = None
        self.thread = None
    
    def execute(self):
        """Execute the verification task"""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
        
        try:
            logger.info(f"Executing task {self.task_id} ({self.task_type})")
            self.result = self.execute_fn(**self.execute_args)
            self.status = TaskStatus.COMPLETED
            logger.info(f"Task {self.task_id} completed successfully")
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error_message = str(e)
            logger.error(f"Task {self.task_id} failed: {self.error_message}", exc_info=True)
        finally:
            self.completed_at = datetime.utcnow()


class VerificationTaskManager:
    """Manages parallel execution of verification tasks using threads.
    
    This manager spawns background threads for parallel verification activities
    and tracks their progress and results.
    """
    
    def __init__(self):
        """Initialize the task manager"""
        self.tasks: Dict[str, VerificationTask] = {}
        self.lock = threading.Lock()
        logger.info("VerificationTaskManager initialized")
    
    def add_task(
        self,
        task_id: str,
        task_type: str,
        target_id: str,
        execute_fn: Callable,
        execute_args: Dict[str, Any]
    ) -> VerificationTask:
        """Add a verification task to the manager.
        
        Args:
            task_id: Unique identifier for the task
            task_type: Type of verification task
            target_id: ID of the record being verified
            execute_fn: Function to execute for verification
            execute_args: Arguments to pass to execute_fn
        
        Returns:
            VerificationTask instance
        """
        with self.lock:
            task = VerificationTask(
                task_id=task_id,
                task_type=task_type,
                target_id=target_id,
                execute_fn=execute_fn,
                execute_args=execute_args
            )
            self.tasks[task_id] = task
            logger.info(f"Added task {task_id} ({task_type})")
            return task
    
    def execute_task(self, task_id: str) -> None:
        """Execute a single task in a background thread.
        
        Args:
            task_id: ID of the task to execute
        """
        with self.lock:
            if task_id not in self.tasks:
                logger.error(f"Task {task_id} not found")
                return
            
            task = self.tasks[task_id]
            
            if task.status != TaskStatus.PENDING:
                logger.warning(f"Task {task_id} already started or completed")
                return
            
            # Create and start thread
            thread = threading.Thread(target=task.execute, daemon=True)
            task.thread = thread
            thread.start()
            logger.info(f"Started thread for task {task_id}")
    
    def execute_all_tasks(self) -> None:
        """Execute all pending tasks in parallel threads"""
        with self.lock:
            pending_tasks = [
                task for task in self.tasks.values()
                if task.status == TaskStatus.PENDING
            ]
        
        logger.info(f"Executing {len(pending_tasks)} pending tasks in parallel")
        
        for task in pending_tasks:
            self.execute_task(task.task_id)
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> None:
        """Wait for all tasks to complete.
        
        Args:
            timeout: Maximum time to wait in seconds (None = wait indefinitely)
        """
        logger.info(f"Waiting for all tasks to complete (timeout: {timeout}s)")
        
        with self.lock:
            threads = [task.thread for task in self.tasks.values() if task.thread]
        
        for thread in threads:
            if thread and thread.is_alive():
                thread.join(timeout=timeout)
        
        logger.info("All tasks completed or timed out")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task.
        
        Args:
            task_id: ID of the task
        
        Returns:
            Dictionary with task status information or None if not found
        """
        with self.lock:
            if task_id not in self.tasks:
                return None
            
            task = self.tasks[task_id]
            return {
                'task_id': task.task_id,
                'task_type': task.task_type,
                'target_id': task.target_id,
                'status': task.status.value,
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'error_message': task.error_message
            }
    
    def get_all_tasks_status(self) -> List[Dict[str, Any]]:
        """Get status of all tasks.
        
        Returns:
            List of task status dictionaries
        """
        with self.lock:
            return [
                self.get_task_status(task_id)
                for task_id in self.tasks.keys()
            ]
    
    def get_completed_tasks(self) -> List[VerificationTask]:
        """Get all completed tasks.
        
        Returns:
            List of completed VerificationTask instances
        """
        with self.lock:
            return [
                task for task in self.tasks.values()
                if task.status == TaskStatus.COMPLETED
            ]
    
    def get_failed_tasks(self) -> List[VerificationTask]:
        """Get all failed tasks.
        
        Returns:
            List of failed VerificationTask instances
        """
        with self.lock:
            return [
                task for task in self.tasks.values()
                if task.status == TaskStatus.FAILED
            ]
    
    def get_task_results(self) -> Dict[str, Any]:
        """Get results from all completed tasks.
        
        Returns:
            Dictionary mapping task_id to result
        """
        with self.lock:
            return {
                task.task_id: task.result
                for task in self.tasks.values()
                if task.status == TaskStatus.COMPLETED and task.result
            }
    
    def is_all_completed(self) -> bool:
        """Check if all tasks are completed (success or failure).
        
        Returns:
            True if all tasks are completed, False otherwise
        """
        with self.lock:
            return all(
                task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                for task in self.tasks.values()
            )
    
    def get_progress(self) -> Dict[str, Any]:
        """Get overall progress statistics.
        
        Returns:
            Dictionary with progress information
        """
        with self.lock:
            total = len(self.tasks)
            completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
            failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
            in_progress = sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS)
            pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
            
            return {
                'total': total,
                'completed': completed,
                'failed': failed,
                'in_progress': in_progress,
                'pending': pending,
                'completion_percentage': (completed + failed) / total * 100 if total > 0 else 0
            }
    
    def clear_tasks(self) -> None:
        """Clear all tasks from the manager"""
        with self.lock:
            self.tasks.clear()
            logger.info("All tasks cleared")
