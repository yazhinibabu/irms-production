"""
C/C++ Language Handler
Analyzes C/C++ code using regex patterns
"""

import re
import logging
from typing import Dict, Any, List
from core.modules.languages.base import LanguageHandler

logger = logging.getLogger(__name__)

class CppHandler(LanguageHandler):
    """
    Handler for C/C++ code analysis
    """
    
    async def analyze(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze C/C++ file
        """
        content = file_info.get("content", "")
        
        components = self.extract_components(content)
        dependencies = self.extract_dependencies(content)
        complexity = self._estimate_complexity(content)
        
        return {
            "components": components,
            "dependencies": dependencies,
            "complexity": complexity
        }
    
    def extract_dependencies(self, content: str) -> List[str]:
        """
        Extract includes from C/C++ code
        """
        dependencies = []
        
        # Match #include statements
        include_pattern = r'#include\s+[<"]([^>"]+)[>"]'
        matches = re.findall(include_pattern, content)
        
        return list(set(matches))
    
    def extract_components(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract functions and classes
        """
        components = []
        
        # Function declarations (simplified)
        func_pattern = r'(?:[\w:]+\s+)?(\w+)\s*\([^)]*\)\s*\{'
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            # Filter out keywords
            if func_name not in ['if', 'for', 'while', 'switch', 'catch']:
                components.append({
                    "name": func_name,
                    "type": "function",
                    "lines": 0
                })
        
        # Class declarations
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            components.append({
                "name": match.group(1),
                "type": "class",
                "lines": 0
            })
        
        # Struct declarations
        struct_pattern = r'struct\s+(\w+)'
        for match in re.finditer(struct_pattern, content):
            components.append({
                "name": match.group(1),
                "type": "struct",
                "lines": 0
            })
        
        return components
    
    def _estimate_complexity(self, content: str) -> float:
        """
        Estimate complexity
        """
        complexity = 1
        
        patterns = [r'\bif\s*\(', r'\bfor\s*\(', r'\bwhile\s*\(', 
                   r'\bswitch\s*\(', r'\bcatch\s*\(']
        
        for pattern in patterns:
            complexity += len(re.findall(pattern, content))
        
        return complexity