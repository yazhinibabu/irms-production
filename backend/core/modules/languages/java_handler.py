"""
Java Language Handler
Analyzes Java code using regex patterns
"""

import re
import logging
from typing import Dict, Any, List
from core.modules.languages.base import LanguageHandler

logger = logging.getLogger(__name__)

class JavaHandler(LanguageHandler):
    """
    Handler for Java code analysis
    """
    
    async def analyze(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Java file
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
        Extract imports from Java code
        """
        dependencies = []
        
        # Match import statements
        import_pattern = r'import\s+([\w.]+);'
        matches = re.findall(import_pattern, content)
        
        return list(set(matches))
    
    def extract_components(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract classes and methods
        """
        components = []
        
        # Match class declarations
        class_pattern = r'(?:public\s+)?(?:abstract\s+)?class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            components.append({
                "name": match.group(1),
                "type": "class",
                "lines": 0
            })
        
        # Match method declarations
        method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:\w+\s+)?(\w+)\s*\([^)]*\)\s*\{'
        for match in re.finditer(method_pattern, content):
            method_name = match.group(1)
            if method_name not in ['if', 'for', 'while', 'switch']:
                components.append({
                    "name": method_name,
                    "type": "method",
                    "lines": 0
                })
        
        return components
    
    def _estimate_complexity(self, content: str) -> float:
        """
        Estimate complexity based on control structures
        """
        complexity = 1
        
        # Count control structures
        patterns = [r'\bif\s*\(', r'\bfor\s*\(', r'\bwhile\s*\(', 
                   r'\bswitch\s*\(', r'\bcatch\s*\(']
        
        for pattern in patterns:
            complexity += len(re.findall(pattern, content))
        
        return complexity