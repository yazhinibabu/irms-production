"""
API Routes for IRMS
Handles all HTTP endpoints with file upload support
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Response, File, UploadFile
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
from models.schemas import AnalysisRequest, AnalysisResponse, HealthResponse, ReportRequest
from services.analysis_service import AnalysisService
from services.ingestion_service import IngestionService
from services.report_service import ReportService
from datetime import datetime
import logging
import io
import traceback
import tempfile
import os
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analysis"])

# In-memory storage for analysis history
analysis_history: List[Dict[str, Any]] = []

@router.post("/analyze")
async def analyze_repository(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze a repository and return comprehensive results
    """
    try:
        logger.info(f"Starting analysis for: {request.repo_path}")
        logger.info(f"User request: {request.user_request}")
        
        # Step 1: Ingest repository
        ingestion_service = IngestionService()
        
        try:
            ingestion_result = await ingestion_service.ingest_repository(request.repo_path)
        except Exception as e:
            logger.error(f"Ingestion failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=400, detail=f"Failed to ingest repository: {str(e)}")
        
        if not ingestion_result or ingestion_result.get("total_files", 0) == 0:
            raise HTTPException(status_code=400, detail="No files found in repository")
        
        logger.info(f"Ingested {ingestion_result.get('total_files', 0)} files")
        
        # Step 2: Analyze
        analysis_service = AnalysisService()
        
        try:
            analysis_result = await analysis_service.analyze(
                ingestion_result,
                user_request=request.user_request,
                enable_ai=request.enable_ai
            )
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
        
        # Step 3: Generate reports
        report_service = ReportService()
        
        try:
            reports = await report_service.generate_reports(analysis_result)
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            logger.error(traceback.format_exc())
            reports = {"error": str(e)}
        
        # Calculate enhanced metrics
        total_files = ingestion_result.get("total_files", 0)
        risk_score = min(analysis_result.get("risk_score", 0), 100)
        
        # Get file details
        file_details = analysis_result.get("file_details", [])
        
        # Calculate gate statistics
        files_passed = len([f for f in file_details if f.get("gate_decision") == "PASS"])
        files_warned = len([f for f in file_details if f.get("gate_decision") == "WARN"])
        files_blocked = len([f for f in file_details if f.get("gate_decision") == "BLOCK"])
        
        # Calculate change statistics
        total_changes = sum(f.get("changes", {}).get("total", 0) for f in file_details)
        total_lines_added = sum(f.get("changes", {}).get("added", 0) for f in file_details)
        total_lines_deleted = sum(f.get("changes", {}).get("deleted", 0) for f in file_details)
        total_lines_modified = sum(f.get("changes", {}).get("modified", 0) for f in file_details)
        
        # Combine results
        final_result = {
            "repo_path": request.repo_path,
            "user_request": request.user_request,
            "timestamp": datetime.now().isoformat(),
            "total_files": total_files,
            "files_passed": files_passed,
            "files_warned": files_warned,
            "files_blocked": files_blocked,
            "languages": ingestion_result.get("languages", {}),
            "code_analysis": analysis_result.get("code_analysis", {}),
            "security": analysis_result.get("security", {}),
            "changes": {
                "total": total_changes,
                "lines_added": total_lines_added,
                "lines_deleted": total_lines_deleted,
                "lines_modified": total_lines_modified,
                "by_type": analysis_result.get("changes", {}).get("by_type", {}),
                "recent": analysis_result.get("changes", {}).get("recent", [])
            },
            "risks": analysis_result.get("risks", []),
            "risk_score": round(risk_score, 2),
            "reports": reports,
            "ai_insights": analysis_result.get("ai_insights", {}) if request.enable_ai else {},
            "file_details": file_details
        }
        
        # Store in history
        analysis_history.append(final_result)
        
        logger.info(f"Analysis completed successfully for: {request.repo_path}")
        
        return final_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analysis: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze-files")
async def analyze_uploaded_files(
    files: List[UploadFile] = File(...),
    user_request: str = "",
    enable_ai: bool = False
):
    """
    Analyze uploaded files directly
    """
    try:
        logger.info(f"Analyzing {len(files)} uploaded files")
        
        # Create temporary directory for uploaded files
        temp_dir = tempfile.mkdtemp(prefix="irms_upload_")
        logger.info(f"Created temp directory: {temp_dir}")
        
        uploaded_file_paths = []
        
        # Save uploaded files
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            content = await file.read()
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            uploaded_file_paths.append(file_path)
            logger.info(f"Saved uploaded file: {file.filename}")
        
        # Ingest only the uploaded files
        ingestion_service = IngestionService()
        ingestion_result = await ingestion_service.ingest_uploaded_files(uploaded_file_paths)
        
        if not ingestion_result or ingestion_result.get("total_files", 0) == 0:
            raise HTTPException(status_code=400, detail="No valid files uploaded")
        
        # Analyze
        analysis_service = AnalysisService()
        analysis_result = await analysis_service.analyze(
            ingestion_result,
            user_request=user_request,
            enable_ai=enable_ai
        )
        
        # Generate reports
        report_service = ReportService()
        reports = await report_service.generate_reports(analysis_result)
        
        # Prepare response (same as analyze_repository)
        file_details = analysis_result.get("file_details", [])
        files_passed = len([f for f in file_details if f.get("gate_decision") == "PASS"])
        files_warned = len([f for f in file_details if f.get("gate_decision") == "WARN"])
        files_blocked = len([f for f in file_details if f.get("gate_decision") == "BLOCK"])
        
        final_result = {
            "repo_path": "Uploaded Files",
            "user_request": user_request,
            "timestamp": datetime.now().isoformat(),
            "total_files": ingestion_result.get("total_files", 0),
            "files_passed": files_passed,
            "files_warned": files_warned,
            "files_blocked": files_blocked,
            "languages": ingestion_result.get("languages", {}),
            "code_analysis": analysis_result.get("code_analysis", {}),
            "security": analysis_result.get("security", {}),
            "changes": {
                "total": 0,
                "lines_added": 0,
                "lines_deleted": 0,
                "lines_modified": 0,
                "by_type": {},
                "recent": []
            },
            "risks": analysis_result.get("risks", []),
            "risk_score": round(analysis_result.get("risk_score", 0), 2),
            "reports": reports,
            "ai_insights": analysis_result.get("ai_insights", {}) if enable_ai else {},
            "file_details": file_details
        }
        
        # Cleanup temp directory
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        return final_result
        
    except Exception as e:
        logger.error(f"File upload analysis failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/generate-report")
async def generate_report(request: ReportRequest):
    """
    Generate downloadable report in specified format
    """
    try:
        results = request.results
        
        report_service = ReportService()
        
        if request.format == "pdf":
            pdf_content = await report_service.generate_pdf_report(results)
            
            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=IRMS_Report.pdf"}
            )
        else:
            md_content = await report_service.generate_markdown_report(results)
            
            return Response(
                content=md_content.encode('utf-8'),
                media_type="text/markdown",
                headers={"Content-Disposition": "attachment; filename=IRMS_Report.md"}
            )
        
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.get("/history")
async def get_analysis_history():
    """Get analysis history"""
    return analysis_history

@router.delete("/history")
async def clear_history():
    """Clear analysis history"""
    global analysis_history
    analysis_history = []
    return {"message": "History cleared"}

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    from core.config import settings
    
    return {
        "status": "healthy",
        "ai_enabled": settings.AI_ENABLED,
        "timestamp": datetime.now().isoformat()
    }