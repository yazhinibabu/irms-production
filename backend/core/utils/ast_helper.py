"""
AST Helper Utilities
Helper functions for AST manipulation
"""

import ast
import logging
from typing import Any, List

logger = logging.getLogger(__name__)

class ASTHelper:
    """
    Helper utilities for AST operations
    """
    
    @staticmethod
    def get_function_names(tree: ast.AST) -> List[str]:
        """
        Extract all function names from AST
        """
        names = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                names.append(node.name)
        
        return names
    
    @staticmethod
    def get_class_names(tree: ast.AST) -> List[str]:
        """
        Extract all class names from AST
        """
        names = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                names.append(node.name)
        
        return names
    
    @staticmethod
    def count_nodes(tree: ast.AST, node_type: type) -> int:
        """
        Count nodes of specific type
        """
        count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, node_type):
                count += 1
        
        return count