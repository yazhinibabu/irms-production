"""
Code Analyzer Module
Analyzes code structure, complexity, and dependencies
"""

import logging
import ast
import re
from typing import Dict, Any, List
from core.modules.languages.language_registry import LanguageRegistry

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """
    Analyzes code structure and extracts insights
    Uses language-specific handlers for detailed analysis
    """
    
    def __init__(self):
        self.registry = LanguageRegistry()
    
    async def analyze(self, ingestion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code structure and complexity
        
        Args:
            ingestion_data: Data from ingestion service
        
        Returns:
            Code analysis results
        """
        logger.info("Analyzing code structure...")
        
        files = ingestion_data.get("files", [])
        
        components = []
        dependencies = set()
        complexity_scores = []
        
        for file_info in files:
            try:
                language = file_info.get("language", "Unknown")
                handler = self.registry.get_handler(language)
                
                if handler:
                    # Use language-specific handler
                    analysis = await handler.analyze(file_info)
                    
                    components.extend(analysis.get("components", []))
                    dependencies.update(analysis.get("dependencies", []))
                    
                    if analysis.get("complexity"):
                        complexity_scores.append(analysis["complexity"])
                else:
                    # Fallback: basic analysis
                    basic = self._basic_analysis(file_info)
                    components.extend(basic.get("components", []))
                    
            except Exception as e:
                logger.warning(f"Failed to analyze {file_info.get('path')}: {e}")
        
        # Calculate metrics
        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
        max_complexity = max(complexity_scores) if complexity_scores else 0
        
        return {
            "components": components[:100],  # Limit output
            "total_components": len(components),
            "dependencies": list(dependencies)[:50],
            "complexity": {
                "average": round(avg_complexity, 2),
                "max": round(max_complexity, 2),
                "samples": len(complexity_scores)
            }
        }
    
    def _basic_analysis(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Basic analysis for unsupported languages
        """
        content = file_info.get("content", "")
        
        # Count functions (basic heuristic)
        function_patterns = [
            r'\bdef\s+(\w+)',  # Python
            r'\bfunction\s+(\w+)',  # JavaScript
            r'\b\w+\s+\w+\s*\([^)]*\)\s*\{',  # C/Java style
        ]
        
        functions = []
        for pattern in function_patterns:
            matches = re.findall(pattern, content)
            functions.extend(matches)
        
        return {
            "components": [
                {
                    "name": func,
                    "type": "function",
                    "file": file_info.get("path", ""),
                    "lines": 0
                }
                for func in functions[:10]
            ]
        }