"""
Ingestion Service
Handles repository ingestion and file upload parsing
"""

import logging
from typing import Dict, Any, List
from pathlib import Path
from core.modules.ingestion import RepositoryIngestion
import traceback

logger = logging.getLogger(__name__)

class IngestionService:
    """
    Service for ingesting and parsing repositories
    """
    
    def __init__(self):
        self.ingestion = RepositoryIngestion()
    
    async def ingest_repository(self, repo_path: str) -> Dict[str, Any]:
        """
        Ingest a repository and extract all relevant information
        """
        logger.info(f"Ingesting repository: {repo_path}")
        
        try:
            path = Path(repo_path)
            
            if repo_path == "." or repo_path == "./":
                path = Path.cwd()
                logger.info(f"Using current directory: {path}")
            
            if not path.exists():
                raise ValueError(f"Repository path does not exist: {repo_path}")
            
            if not path.is_dir():
                raise ValueError(f"Path is not a directory: {repo_path}")
            
            result = await self.ingestion.ingest(str(path.resolve()))
            
            if not result or result.get("total_files", 0) == 0:
                logger.warning(f"No files found in: {repo_path}")
                raise ValueError(f"No supported files found in directory: {repo_path}")
            
            logger.info(f"Ingestion complete: {result.get('total_files', 0)} files processed")
            return result
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Failed to ingest repository: {str(e)}")
    
    async def ingest_uploaded_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Ingest specific uploaded files only
        """
        logger.info(f"Ingesting {len(file_paths)} uploaded files")
        
        try:
            result = await self.ingestion.ingest_specific_files(file_paths)
            
            if not result or result.get("total_files", 0) == 0:
                raise ValueError("No valid files to analyze")
            
            logger.info(f"Uploaded file ingestion complete: {result.get('total_files', 0)} files")
            return result
            
        except Exception as e:
            logger.error(f"Uploaded file ingestion failed: {e}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Failed to ingest uploaded files: {str(e)}")