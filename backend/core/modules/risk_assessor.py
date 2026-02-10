"""
Risk Assessor Module
Assesses release risks based on analysis results
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class RiskAssessor:
    """
    Assesses risks for the release
    Combines findings from various analysis modules
    """
    
    async def assess(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess release risks
        
        Args:
            analysis_results: Combined analysis results
        
        Returns:
            Risk assessment with score and prioritized risks
        """
        logger.info("Assessing risks...")
        
        risks = []
        risk_score = 0.0
        
        # Security risks
        security_risks = self._assess_security_risks(analysis_results)
        risks.extend(security_risks["risks"])
        risk_score += security_risks["score"]
        
        # Complexity risks
        complexity_risks = self._assess_complexity_risks(analysis_results)
        risks.extend(complexity_risks["risks"])
        risk_score += complexity_risks["score"]
        
        # Change risks
        change_risks = self._assess_change_risks(analysis_results)
        risks.extend(change_risks["risks"])
        risk_score += change_risks["score"]
        
        # Normalize score to 0-10
        risk_score = min(risk_score, 10.0)
        
        # Sort by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        risks.sort(key=lambda x: priority_order.get(x.get("priority", "LOW"), 4))
        
        return {
            "score": round(risk_score, 2),
            "risks": risks,
            "risk_level": self._get_risk_level(risk_score)
        }
    
    def _assess_security_risks(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess security-related risks
        """
        security = results.get("security", {})
        risks = []
        score = 0.0
        
        vulnerabilities = security.get("vulnerabilities", [])
        secrets = security.get("secrets_found", [])
        
        # Critical vulnerabilities
        critical_vulns = [v for v in vulnerabilities if v.get("severity") == "CRITICAL"]
        if critical_vulns:
            risks.append({
                "priority": "CRITICAL",
                "title": f"{len(critical_vulns)} Critical Security Vulnerabilities",
                "description": "Critical security vulnerabilities must be fixed before release",
                "mitigation": "Review and fix all critical vulnerabilities immediately"
            })
            score += 3.0
        
        # High vulnerabilities
        high_vulns = [v for v in vulnerabilities if v.get("severity") == "HIGH"]
        if high_vulns:
            risks.append({
                "priority": "HIGH",
                "title": f"{len(high_vulns)} High Severity Vulnerabilities",
                "description": "High severity security issues detected",
                "mitigation": "Address high severity issues before release"
            })
            score += 2.0
        
        # Secrets in code
        if secrets:
            risks.append({
                "priority": "CRITICAL",
                "title": f"{len(secrets)} Potential Secrets Detected",
                "description": "Hardcoded secrets found in code",
                "mitigation": "Remove all secrets and use environment variables or secret management"
            })
            score += 2.5
        
        return {"risks": risks, "score": score}
    
    def _assess_complexity_risks(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess complexity-related risks
        """
        code_analysis = results.get("code_analysis", {})
        complexity = code_analysis.get("complexity", {})
        
        risks = []
        score = 0.0
        
        max_complexity = complexity.get("max", 0)
        avg_complexity = complexity.get("average", 0)
        
        if max_complexity > 20:
            risks.append({
                "priority": "HIGH",
                "title": "High Code Complexity Detected",
                "description": f"Maximum complexity score of {max_complexity} indicates potential maintainability issues",
                "mitigation": "Refactor complex functions to improve maintainability"
            })
            score += 1.5
        
        if avg_complexity > 10:
            risks.append({
                "priority": "MEDIUM",
                "title": "Above Average Code Complexity",
                "description": f"Average complexity of {avg_complexity} may impact long-term maintenance",
                "mitigation": "Consider simplifying code structure where possible"
            })
            score += 1.0
        
        return {"risks": risks, "score": score}
    
    def _assess_change_risks(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess change-related risks
        """
        changes = results.get("changes", {})
        risks = []
        score = 0.0
        
        total_changes = changes.get("total", 0)
        
        if total_changes > 100:
            risks.append({
                "priority": "MEDIUM",
                "title": "Large Number of Changes",
                "description": f"{total_changes} files changed - increases testing scope",
                "mitigation": "Ensure comprehensive testing coverage for all changes"
            })
            score += 1.0
        
        return {"risks": risks, "score": score}
    
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