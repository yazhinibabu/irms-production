"""
Repository Ingestion Module
Handles scanning and parsing of repositories
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List,Optional
import chardet

logger = logging.getLogger(__name__)

class RepositoryIngestion:
    """
    Handles repository ingestion and file scanning
    """
    
    SUPPORTED_EXTENSIONS = {
        '.py', '.java', '.js', '.jsx', '.ts', '.tsx',
        '.c', '.cpp', '.cc', '.h', '.hpp',
        '.go', '.rs', '.rb', '.php',
        '.html', '.css', '.scss', '.sass',
        '.json', '.xml', '.yaml', '.yml',
        '.md', '.txt', '.sh', '.bat'
    }
    
    IGNORE_DIRS = {
        'node_modules', '__pycache__', '.git', '.svn',
        'venv', 'env', 'build', 'dist', 'target',
        '.idea', '.vscode', 'bin', 'obj'
    }
    
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    async def ingest(self, repo_path: str) -> Dict[str, Any]:
        """
        Ingest repository and extract information
        """
        path = Path(repo_path)
        
        if not path.exists():
            raise ValueError(f"Path does not exist: {repo_path}")
        
        files = []
        languages = {}
        total_lines = 0
        
        # Scan directory
        for file_path in self._scan_directory(path):
            try:
                file_info = self._process_file(file_path)
                if file_info:
                    files.append(file_info)
                    
                    lang = file_info.get("language", "unknown")
                    languages[lang] = languages.get(lang, 0) + 1
                    
                    total_lines += file_info.get("lines", 0)
                    
            except Exception as e:
                logger.warning(f"Failed to process file {file_path}: {e}")
        
        return {
            "repo_path": str(path),
            "total_files": len(files),
            "total_lines": total_lines,
            "languages": languages,
            "files": files
        }
    
    async def ingest_specific_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Ingest only specific files (for uploads)
        """
        files = []
        languages = {}
        total_lines = 0
        
        for file_path in file_paths:
            try:
                path = Path(file_path)
                if path.exists() and path.is_file():
                    file_info = self._process_file(path)
                    if file_info:
                        files.append(file_info)
                        
                        lang = file_info.get("language", "unknown")
                        languages[lang] = languages.get(lang, 0) + 1
                        
                        total_lines += file_info.get("lines", 0)
                        
            except Exception as e:
                logger.warning(f"Failed to process uploaded file {file_path}: {e}")
        
        return {
            "repo_path": "Uploaded Files",
            "total_files": len(files),
            "total_lines": total_lines,
            "languages": languages,
            "files": files
        }
    
    def _scan_directory(self, path: Path) -> List[Path]:
        """
        Recursively scan directory for supported files
        """
        files = []
        
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    if any(ignore_dir in item.parts for ignore_dir in self.IGNORE_DIRS):
                        continue
                    
                    if item.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                        if item.stat().st_size <= self.max_file_size:
                            files.append(item)
        
        except Exception as e:
            logger.error(f"Error scanning directory {path}: {e}")
        
        return files
    
    def _process_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Process individual file
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'
            
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            return {
                "path": str(file_path),
                "name": file_path.name,
                "language": self._detect_language(file_path),
                "extension": file_path.suffix,
                "size": file_path.stat().st_size,
                "lines": len(lines),
                "content": content
            }
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return None
    
    def _detect_language(self, file_path: Path) -> str:
        """
        Detect programming language from file extension
        """
        ext = file_path.suffix.lower()
        
        language_map = {
            '.py': 'Python',
            '.java': 'Java',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript',
            '.c': 'C',
            '.cpp': 'C++',
            '.cc': 'C++',
            '.h': 'C/C++',
            '.hpp': 'C++',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.json': 'JSON',
            '.xml': 'XML',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.md': 'Markdown',
            '.sh': 'Shell',
        }
        
        return language_map.get(ext, 'Unknown')