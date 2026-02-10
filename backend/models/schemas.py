"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class AnalysisRequest(BaseModel):
    """Request schema for repository analysis"""
    repo_path: str = Field(..., description="Path to repository")
    user_request: str = Field(default="", description="User's request/description of changes")
    enable_ai: bool = Field(default=False, description="Enable AI-powered insights")

class ReportRequest(BaseModel):
    """Request schema for report generation"""
    results: Dict[str, Any] = Field(..., description="Analysis results")
    format: str = Field(default="markdown", description="Report format: markdown or pdf")

class IssueInfo(BaseModel):
    """Code issue information"""
    line: int
    description: str
    severity: str  # critical, high, medium, low

class FileDetailInfo(BaseModel):
    """Detailed file analysis information"""
    name: str
    path: str
    language: str
    lines: int
    risk_score: float
    gate_decision: str  # PASS, WARN, BLOCK
    maintainability: float
    complexity: float
    issues: List[Dict[str, Any]]
    changes: Dict[str, int]
    risk_breakdown: Dict[str, float]
    recommendations: List[str]
    modified_code: str = ""

class AnalysisResponse(BaseModel):
    """Response schema for repository analysis"""
    repo_path: str
    user_request: str
    timestamp: str
    total_files: int
    files_passed: int
    files_warned: int
    files_blocked: int
    languages: Dict[str, int]
    code_analysis: Dict[str, Any]
    security: Dict[str, Any]
    changes: Dict[str, Any]
    risks: List[Dict[str, Any]]
    risk_score: float
    reports: Dict[str, Any]
    ai_insights: Dict[str, Any] = {}
    file_details: List[Dict[str, Any]] = []

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    ai_enabled: bool
    timestamp: str