"""
Report Generator Module
Generates various reports and documentation
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Generates reports and documentation
    """
    
    async def generate_release_notes(self, results: Dict[str, Any]) -> str:
        """
        Generate release notes
        """
        changes = results.get("changes", {})
        risk_score = results.get("risk_score", 0)
        
        notes = f"""# Release Notes

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overview

- **Total Files Changed:** {changes.get('total', 0)}
- **Risk Score:** {risk_score}/10
- **Risk Level:** {self._get_risk_level(risk_score)}

## Changes Summary

"""
        
        by_type = changes.get("by_type", {})
        for change_type, count in by_type.items():
            notes += f"- **{change_type.title()}:** {count} files\n"
        
        # Add AI insights if available
        ai_insights = results.get("ai_insights", {})
        if ai_insights and ai_insights.get("release_recommendations"):
            notes += f"\n## AI Insights\n\n{ai_insights['release_recommendations']}\n"
        
        return notes
    
    async def generate_security_report(self, results: Dict[str, Any]) -> str:
        """
        Generate security report
        """
        security = results.get("security", {})
        
        report = f"""# Security Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

"""
        
        vulnerabilities = security.get("vulnerabilities", [])
        secrets = security.get("secrets_found", [])
        
        report += f"- **Vulnerabilities:** {len(vulnerabilities)}\n"
        report += f"- **Potential Secrets:** {len(secrets)}\n\n"
        
        if vulnerabilities:
            report += "## Vulnerabilities\n\n"
            
            for vuln in vulnerabilities[:10]:
                report += f"### {vuln.get('severity', 'UNKNOWN')} - {vuln.get('description', 'N/A')}\n\n"
                report += f"- **File:** `{vuln.get('file', 'N/A')}`\n"
                report += f"- **Line:** {vuln.get('line', 'N/A')}\n"
                if vuln.get("recommendation"):
                    report += f"- **Recommendation:** {vuln['recommendation']}\n"
                report += "\n"
        
        if secrets:
            report += "## Potential Secrets\n\n"
            report += "⚠️ The following files may contain hardcoded secrets:\n\n"
            
            for secret in secrets[:10]:
                report += f"- `{secret.get('file', 'N/A')}` (Line {secret.get('line', 'N/A')})\n"
        
        # Add AI insights if available
        ai_insights = results.get("ai_insights", {})
        if ai_insights and ai_insights.get("security_recommendations"):
            report += f"\n## AI Security Recommendations\n\n{ai_insights['security_recommendations']}\n"
        
        return report
    
    async def generate_checklist(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate release checklist
        """
        checklist = []
        
        # Security checks
        security = results.get("security", {})
        if security.get("vulnerabilities"):
            checklist.append({
                "id": "sec-1",
                "item": "Review and fix all security vulnerabilities",
                "priority": "HIGH"
            })
        
        if security.get("secrets_found"):
            checklist.append({
                "id": "sec-2",
                "item": "Remove all hardcoded secrets from code",
                "priority": "CRITICAL"
            })
        
        # Risk checks
        risks = results.get("risks", [])
        for idx, risk in enumerate(risks[:5]):
            checklist.append({
                "id": f"risk-{idx}",
                "item": risk.get("title", "N/A"),
                "priority": risk.get("priority", "MEDIUM")
            })
        
        # Standard checks
        checklist.extend([
            {
                "id": "std-1",
                "item": "Run all unit tests",
                "priority": "HIGH"
            },
            {
                "id": "std-2",
                "item": "Run integration tests",
                "priority": "HIGH"
            },
            {
                "id": "std-3",
                "item": "Update documentation",
                "priority": "MEDIUM"
            },
            {
                "id": "std-4",
                "item": "Review release notes",
                "priority": "MEDIUM"
            },
            {
                "id": "std-5",
                "item": "Backup production data",
                "priority": "HIGH"
            }
        ])
        
        return checklist
    
    def _get_risk_level(self, score: float) -> str:
        """
        Get risk level based on score
        """
        if score >= 7.0:
            return "HIGH"
        elif score >= 4.0:
            return "MEDIUM"
        else:
            return "LOW"