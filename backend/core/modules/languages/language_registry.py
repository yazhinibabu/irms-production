"""
Language Registry
Central registry for language handlers
"""

import logging
from typing import Dict, Optional
from core.modules.languages.base import LanguageHandler
from core.modules.languages.python_handler import PythonHandler
from core.modules.languages.java_handler import JavaHandler
from core.modules.languages.javascript_handler import JavaScriptHandler
from core.modules.languages.cpp_handler import CppHandler

logger = logging.getLogger(__name__)

class LanguageRegistry:
    """
    Registry for language-specific handlers
    Allows easy addition of new language support
    """
    
    def __init__(self):
        self.handlers: Dict[str, LanguageHandler] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """
        Register default language handlers
        """
        self.register("Python", PythonHandler())
        self.register("Java", JavaHandler())
        self.register("JavaScript", JavaScriptHandler())
        self.register("TypeScript", JavaScriptHandler())  # Reuse JS handler
        self.register("C", CppHandler())
        self.register("C++", CppHandler())
        
        logger.info(f"Registered {len(self.handlers)} language handlers")
    
    def register(self, language: str, handler: LanguageHandler):
        """
        Register a new language handler
        
        Args:
            language: Language name
            handler: Handler instance
        """
        self.handlers[language] = handler
        logger.debug(f"Registered handler for {language}")
    
    def get_handler(self, language: str) -> Optional[LanguageHandler]:
        """
        Get handler for a language
        
        Args:
            language: Language name
        
        Returns:
            Handler instance or None
        """
        return self.handlers.get(language)
    
    def list_supported_languages(self) -> list:
        """
        Get list of supported languages
        """
        return list(self.handlers.keys())