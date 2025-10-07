"""Base Workflow Class"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging


class BaseWorkflow(ABC):
    """Abstract base class for all workflows"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the workflow with configuration
        
        Args:
            config: Configuration dictionary for the workflow
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for the workflow"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """
        Execute the workflow
        
        Args:
            input_data: Input data for the workflow
            
        Returns:
            Output data from the workflow
        """
        pass
    
    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data for the workflow
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the workflow
        
        Returns:
            Status dictionary
        """
        return {
            "workflow": self.__class__.__name__,
            "config": self.config
        }
