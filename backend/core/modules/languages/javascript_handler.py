"""
JavaScript/TypeScript Language Handler
Analyzes JavaScript code using regex patterns
"""

import re
import logging
from typing import Dict, Any, List
from core.modules.languages.base import LanguageHandler

logger = logging.getLogger(__name__)

class JavaScriptHandler(LanguageHandler):
    """
    Handler for JavaScript/TypeScript code analysis
    """
    
    async def analyze(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze JavaScript/TypeScript file
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
        Extract imports from JavaScript code
        """
        dependencies = []
        
        # ES6 imports
        import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]'
        matches = re.findall(import_pattern, content)
        dependencies.extend(matches)
        
        # CommonJS require
        require_pattern = r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        matches = re.findall(require_pattern, content)
        dependencies.extend(matches)
        
        return list(set(dependencies))
    
    def extract_components(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract functions and classes
        """
        components = []
        
        # Function declarations
        func_pattern = r'function\s+(\w+)\s*\('
        for match in re.finditer(func_pattern, content):
            components.append({
                "name": match.group(1),
                "type": "function",
                "lines": 0
            })
        
        # Arrow functions
        arrow_pattern = r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>'
        for match in re.finditer(arrow_pattern, content):
            components.append({
                "name": match.group(1),
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
        
        # React components
        react_pattern = r'(?:const|function)\s+(\w+)\s*=.*?(?:React\.Component|React\.FC)'
        for match in re.finditer(react_pattern, content):
            components.append({
                "name": match.group(1),
                "type": "component",
                "lines": 0
            })
        
        return components
    
    def _estimate_complexity(self, content: str) -> float:
        """
        Estimate complexity
        """
        complexity = 1
        
        patterns = [r'\bif\s*\(', r'\bfor\s*\(', r'\bwhile\s*\(', 
                   r'\bswitch\s*\(', r'\bcatch\s*\(', r'\?\s*:']
        
        for pattern in patterns:
            complexity += len(re.findall(pattern, content))
        
        return complexity