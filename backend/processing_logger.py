"""
Processing logger for tracking and visualizing internal steps
"""
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .models import ProcessingStep


class ProcessingLogger:
    """
    Logger that tracks processing steps with timing and details
    for visualization and explanation purposes
    """
    
    def __init__(self, job_name: str = "Processing"):
        self.job_name = job_name
        self.steps: List[ProcessingStep] = []
        self.current_step_start: Optional[float] = None
        self.current_step_name: Optional[str] = None
        
        # Setup Python logging
        self.logger = logging.getLogger(f"QGENOME.{job_name}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def start_step(self, step_name: str, details: Dict[str, Any] = None):
        """Start tracking a new processing step"""
        self.current_step_name = step_name
        self.current_step_start = time.time()
        
        log_msg = f"[START] {step_name}"
        if details:
            log_msg += f" | {details}"
        self.logger.info(log_msg)
        
        return self
    
    def end_step(self, status: str = "completed", additional_details: Dict[str, Any] = None):
        """End the current processing step"""
        if self.current_step_start is None:
            return
        
        duration_ms = (time.time() - self.current_step_start) * 1000
        
        step = ProcessingStep(
            step_name=self.current_step_name,
            timestamp=datetime.utcnow(),
            duration_ms=duration_ms,
            details=additional_details or {},
            status=status
        )
        
        self.steps.append(step)
        
        log_msg = f"[END] {self.current_step_name} | Duration: {duration_ms:.2f}ms | Status: {status}"
        if additional_details:
            log_msg += f" | {additional_details}"
        self.logger.info(log_msg)
        
        self.current_step_start = None
        self.current_step_name = None
        
        return step
    
    def log_info(self, message: str, details: Dict[str, Any] = None):
        """Log an info message"""
        log_msg = f"[INFO] {message}"
        if details:
            log_msg += f" | {details}"
        self.logger.info(log_msg)
    
    def log_error(self, message: str, error: Exception = None):
        """Log an error message"""
        log_msg = f"[ERROR] {message}"
        if error:
            log_msg += f" | {str(error)}"
        self.logger.error(log_msg)
    
    def get_steps(self) -> List[ProcessingStep]:
        """Get all recorded processing steps"""
        return self.steps
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all processing steps"""
        total_duration = sum(step.duration_ms or 0 for step in self.steps)
        
        return {
            "job_name": self.job_name,
            "total_steps": len(self.steps),
            "total_duration_ms": total_duration,
            "steps": [
                {
                    "step_name": step.step_name,
                    "duration_ms": step.duration_ms,
                    "status": step.status,
                    "details": step.details
                }
                for step in self.steps
            ]
        }
    
    def reset(self):
        """Reset the logger for a new job"""
        self.steps = []
        self.current_step_start = None
        self.current_step_name = None


# Global logger instance for easy access
_global_logger: Optional[ProcessingLogger] = None


def get_global_logger() -> ProcessingLogger:
    """Get or create the global processing logger"""
    global _global_logger
    if _global_logger is None:
        _global_logger = ProcessingLogger("GlobalProcessor")
    return _global_logger


def create_job_logger(job_name: str) -> ProcessingLogger:
    """Create a new logger for a specific job"""
    return ProcessingLogger(job_name)
