"""
Base Language Handler
Abstract base class for language-specific handlers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class LanguageHandler(ABC):
    """
    Abstract base class for language handlers
    Each language should implement this interface
    """
    
    @abstractmethod
    async def analyze(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a file and extract language-specific information
        
        Args:
            file_info: File information including content and metadata
        
        Returns:
            Dictionary containing:
            - components: List of functions, classes, etc.
            - dependencies: List of imports/dependencies
            - complexity: Complexity metrics
        """
        pass
    
    @abstractmethod
    def extract_dependencies(self, content: str) -> list:
        """
        Extract dependencies from code
        """
        pass
    
    @abstractmethod
    def extract_components(self, content: str) -> list:
        """
        Extract code components (functions, classes, etc.)
        """
        pass