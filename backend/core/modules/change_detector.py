"""
Change Detector Module
Detects and analyzes changes in the codebase
"""

import logging
from typing import Dict, Any, List
from pathlib import Path
import subprocess

logger = logging.getLogger(__name__)

class ChangeDetector:
    """
    Detects changes in the repository
    Uses git if available, otherwise does basic file analysis
    """
    
    async def detect(self, ingestion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect changes in repository
        
        Args:
            ingestion_data: Data from ingestion service
        
        Returns:
            Change detection results
        """
        logger.info("Detecting changes...")
        
        repo_path = ingestion_data.get("repo_path", "")
        
        # Try git-based detection
        git_changes = await self._detect_git_changes(repo_path)
        
        if git_changes:
            return git_changes
        
        # Fallback: basic file analysis
        return self._basic_change_detection(ingestion_data)
    
    async def _detect_git_changes(self, repo_path: str) -> Dict[str, Any]:
        """
        Detect changes using git
        """
        try:
            # Check if git repo
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return None
            
            # Get recent commits
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            commits = result.stdout.strip().split('\n') if result.stdout else []
            
            # Get changed files
            result = subprocess.run(
                ["git", "diff", "--name-status", "HEAD~5..HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            changes = []
            by_type = {"added": 0, "modified": 0, "deleted": 0}
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t', 1)
                    if len(parts) == 2:
                        status, file_path = parts
                        
                        change_type = {
                            'A': 'added',
                            'M': 'modified',
                            'D': 'deleted'
                        }.get(status[0], 'modified')
                        
                        changes.append({
                            "file": file_path,
                            "type": change_type
                        })
                        
                        by_type[change_type] = by_type.get(change_type, 0) + 1
            
            return {
                "total": len(changes),
                "recent": changes[:20],
                "by_type": by_type,
                "commits": len(commits)
            }
            
        except Exception as e:
            logger.debug(f"Git detection failed: {e}")
            return None
    
    def _basic_change_detection(self, ingestion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Basic change detection without git
        """
        files = ingestion_data.get("files", [])
        
        return {
            "total": len(files),
            "recent": [],
            "by_type": {"scanned": len(files)},
            "note": "Git not available - showing file count only"
        }