"""
Python Language Handler
Analyzes Python code using AST
"""

import ast
import logging
from typing import Dict, Any, List
from core.modules.languages.base import LanguageHandler

logger = logging.getLogger(__name__)

class PythonHandler(LanguageHandler):
    """
    Handler for Python code analysis
    """
    
    async def analyze(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Python file
        """
        content = file_info.get("content", "")
        
        try:
            tree = ast.parse(content)
            
            components = self.extract_components(content)
            dependencies = self.extract_dependencies(content)
            complexity = self._calculate_complexity(tree)
            
            return {
                "components": components,
                "dependencies": dependencies,
                "complexity": complexity
            }
            
        except SyntaxError as e:
            logger.warning(f"Python syntax error in {file_info.get('path')}: {e}")
            return {"components": [], "dependencies": [], "complexity": 0}
    
    def extract_dependencies(self, content: str) -> List[str]:
        """
        Extract imports from Python code
        """
        dependencies = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module)
        
        except:
            pass
        
        return list(set(dependencies))
    
    def extract_components(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract functions and classes
        """
        components = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    components.append({
                        "name": node.name,
                        "type": "function",
                        "lines": self._count_lines(node),
                        "arguments": len(node.args.args)
                    })
                elif isinstance(node, ast.ClassDef):
                    components.append({
                        "name": node.name,
                        "type": "class",
                        "lines": self._count_lines(node),
                        "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                    })
        
        except:
            pass
        
        return components
    
    def _calculate_complexity(self, tree: ast.AST) -> float:
        """
        Calculate cyclomatic complexity
        """
        complexity = 1
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _count_lines(self, node: ast.AST) -> int:
        """
        Count lines in AST node
        """
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            return node.end_lineno - node.lineno + 1
        return 0