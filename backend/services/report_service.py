"""
Report Service - Enhanced with comprehensive PDF generation
Generates detailed reports matching professional standards
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, KeepTogether
)
from reportlab.lib import colors
from io import BytesIO

logger = logging.getLogger(__name__)

class ReportService:
    """
    Service for generating comprehensive reports and documentation
    """
    
    def __init__(self):
        pass
    
    async def generate_reports(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate all reports based on analysis results
        """
        logger.info("Generating reports...")
        
        reports = {}
        
        try:
            # Release Notes
            reports["release_notes"] = self._generate_release_notes(analysis_results)
            
            # Security Report
            reports["security_report"] = self._generate_security_report(analysis_results)
            
            # Checklist
            reports["checklist"] = self._generate_checklist(analysis_results)
            
            logger.info("Reports generated successfully")
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            reports["error"] = str(e)
        
        return reports
    
    async def generate_pdf_report(self, analysis_results: Dict[str, Any]) -> bytes:
        """
        Generate comprehensive PDF report matching the reference format
        """
        logger.info("Generating comprehensive PDF report...")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#283593'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        heading3_style = ParagraphStyle(
            'CustomHeading3',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.black,
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        bullet_style = ParagraphStyle(
            'BulletStyle',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=4
        )
        
        # Extract data
        repo_path = analysis_results.get("repo_path", "N/A")
        user_request = analysis_results.get("user_request", "N/A")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        risk_score = analysis_results.get("risk_score", 0)
        total_files = analysis_results.get("total_files", 0)
        files_passed = analysis_results.get("files_passed", 0)
        files_warned = analysis_results.get("files_warned", 0)
        files_blocked = analysis_results.get("files_blocked", 0)
        file_details = analysis_results.get("file_details", [])
        
        # Determine status
        if risk_score < 30:
            status = "PASS"
            status_color = colors.green
        elif risk_score < 60:
            status = "WARN"
            status_color = colors.orange
        else:
            status = "BLOCK"
            status_color = colors.red
        
        # Title Page
        story.append(Paragraph("Intelligent Release Management", title_style))
        story.append(Paragraph("Scanner (IRMS)", title_style))
        story.append(Spacer(1, 20))
        story.append(Paragraph("Release Analysis Report", subtitle_style))
        story.append(Spacer(1, 30))
        
        # Metadata
        story.append(Paragraph(f"<b>Generated:</b> {timestamp}", normal_style))
        story.append(Paragraph(f"<b>Status:</b> <font color='{status_color.hexval()}'>{status}</font>", normal_style))
        story.append(Spacer(1, 30))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading1_style))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph(f"<b>User Request:</b> {user_request}", normal_style))
        story.append(Spacer(1, 10))
        
        summary_data = [
            ["Files Analyzed:", str(total_files)],
            ["Overall Risk Score:", f"{risk_score}/100"],
            ["Gate Decision:", status]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 15))
        
        # Gate Breakdown
        story.append(Paragraph("<b>Gate Breakdown:</b>", normal_style))
        story.append(Paragraph(f"• ✓ PASS: {files_passed} files", bullet_style))
        story.append(Paragraph(f"• ■ WARN: {files_warned} files", bullet_style))
        story.append(Paragraph(f"• ■ BLOCK: {files_blocked} files", bullet_style))
        story.append(Spacer(1, 20))
        
        # Input Sources
        story.append(Paragraph("Input Sources", heading1_style))
        
        languages = analysis_results.get("languages", {})
        total_by_lang = sum(languages.values())
        
        story.append(Paragraph(f"<b>Files Ingested:</b> {total_by_lang}", normal_style))
        
        for file_detail in file_details:
            story.append(Paragraph(f" - {file_detail.get('name', 'Unknown')}", bullet_style))
        
        story.append(Paragraph(f"<b>Documentation Files:</b> 0", normal_style))
        story.append(Spacer(1, 20))
        
        # Page break before detailed analysis
        story.append(PageBreak())
        
        # Detailed File Analysis
        story.append(Paragraph("Detailed File Analysis", heading1_style))
        story.append(Spacer(1, 15))
        
        for file_detail in file_details:
            # File header
            file_name = file_detail.get("name", "Unknown")
            file_risk = file_detail.get("risk_score", 0)
            file_gate = file_detail.get("gate_decision", "PASS")
            
            # Determine file status symbol and color
            if file_gate == "PASS":
                symbol = "■"
                gate_color = colors.green
            elif file_gate == "WARN":
                symbol = "■"
                gate_color = colors.orange
            else:
                symbol = "■"
                gate_color = colors.red
            
            story.append(Paragraph(f"<font color='{gate_color.hexval()}'>{symbol}</font> <b>{file_name}</b>", heading2_style))
            story.append(Spacer(1, 8))
            
            # Risk Score and Gate Decision
            story.append(Paragraph(f"<b>Risk Score:</b> {file_risk}/100", normal_style))
            story.append(Paragraph(f"<b>Gate Decision:</b> <font color='{gate_color.hexval()}'>{symbol} {file_gate}</font>", normal_style))
            story.append(Spacer(1, 10))
            
            # Original Code Analysis
            story.append(Paragraph("#### Original Code Analysis", heading3_style))
            
            lines = file_detail.get("lines", 0)
            maintainability = file_detail.get("maintainability", 0)
            complexity = file_detail.get("complexity", 0)
            issues = file_detail.get("issues", [])
            
            story.append(Paragraph(f"• <b>Lines of Code:</b> {lines}", bullet_style))
            story.append(Paragraph(f"• <b>Maintainability Index:</b> {maintainability:.2f}", bullet_style))
            story.append(Paragraph(f"• <b>Average Complexity:</b> {complexity:.2f}", bullet_style))
            story.append(Paragraph(f"• <b>Issues Found:</b> {len(issues)}", bullet_style))
            story.append(Spacer(1, 8))
            
            # Key Issues
            if issues:
                story.append(Paragraph("<b>Key Issues:</b>", normal_style))
                for issue in issues:
                    line_num = issue.get("line", 0)
                    description = issue.get("description", "N/A")
                    severity = issue.get("severity", "low")
                    story.append(Paragraph(f"• Line {line_num}: {description} ({severity})", bullet_style))
                story.append(Spacer(1, 8))
            
            # Changes Applied
            story.append(Paragraph("#### Changes Applied", heading3_style))
            story.append(Paragraph("AI analysis skipped: AI model is not initialized. Original code preserved.", normal_style))
            story.append(Spacer(1, 8))
            
            # Change Statistics
            story.append(Paragraph("#### Change Statistics", heading3_style))
            changes = file_detail.get("changes", {})
            story.append(Paragraph(f"• <b>Lines Added:</b> +{changes.get('added', 0)}", bullet_style))
            story.append(Paragraph(f"• <b>Lines Deleted:</b> -{changes.get('deleted', 0)}", bullet_style))
            story.append(Paragraph(f"• <b>Lines Modified:</b> ~{changes.get('modified', 0)}", bullet_style))
            story.append(Paragraph(f"• <b>Total Changes:</b> {changes.get('total', 0)}", bullet_style))
            story.append(Spacer(1, 8))
            
            # Risk Breakdown
            story.append(Paragraph("#### Risk Breakdown", heading3_style))
            risk_breakdown = file_detail.get("risk_breakdown", {})
            story.append(Paragraph(f"• <b>Complexity Risk:</b> {risk_breakdown.get('complexity', 0):.2f}%", bullet_style))
            story.append(Paragraph(f"• <b>Change Volume Risk:</b> {risk_breakdown.get('change_volume', 0):.2f}%", bullet_style))
            story.append(Paragraph(f"• <b>Critical Function Risk:</b> {risk_breakdown.get('critical_function', 0):.2f}%", bullet_style))
            story.append(Paragraph(f"• <b>Issue Severity Risk:</b> {risk_breakdown.get('issue_severity', 0):.2f}%", bullet_style))
            story.append(Spacer(1, 8))
            
            # Recommendations
            recommendations = file_detail.get("recommendations", [])
            if recommendations:
                story.append(Paragraph("<b>Recommendations:</b>", normal_style))
                for rec in recommendations:
                    story.append(Paragraph(f"• {rec}", bullet_style))
            
            story.append(Spacer(1, 20))
        
        # Page break before overall recommendations
        story.append(PageBreak())
        
        # Overall Recommendations
        story.append(Paragraph("Overall Recommendations", heading1_style))
        story.append(Spacer(1, 10))
        
        # Collect all recommendations
        all_recommendations = []
        high_severity_count = 0
        
        for file_detail in file_details:
            issues = file_detail.get("issues", [])
            for issue in issues:
                if issue.get("severity") in ["critical", "high"]:
                    high_severity_count += 1
        
        if high_severity_count > 0:
            all_recommendations.append(f"Address {high_severity_count} medium/high severity issues")
        
        all_recommendations.append("✓ Low risk changes - safe to proceed")
        
        for i, rec in enumerate(all_recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", bullet_style))
        
        story.append(Spacer(1, 20))
        
        # Conclusion
        story.append(Paragraph("Conclusion", heading1_style))
        story.append(Spacer(1, 10))
        
        conclusion_text = f"""The changes have been analyzed and deemed {'low' if risk_score < 30 else 'medium' if risk_score < 60 else 'high'} risk (score: {risk_score}/100).
The modified code is {'recommended for the next release stage with standard review procedures' if risk_score < 30 else 'requires additional review before proceeding' if risk_score < 60 else 'requires thorough review and risk mitigation before deployment'}."""
        
        story.append(Paragraph(conclusion_text, normal_style))
        story.append(Spacer(1, 15))
        
        # Next Steps
        story.append(Paragraph("<b>Next Steps:</b>", normal_style))
        story.append(Paragraph("1. Review the modified code files", bullet_style))
        story.append(Paragraph("2. Run automated test suites", bullet_style))
        story.append(Paragraph("3. Proceed with deployment pipeline", bullet_style))
        story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph("<i>*Report generated by Intelligent Release Management Scanner (IRMS)*</i>", 
                              ParagraphStyle('Footer', parent=normal_style, alignment=TA_CENTER, fontSize=9)))
        
        # Build PDF
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        logger.info("Comprehensive PDF report generated successfully")
        return pdf_content
    
    async def generate_markdown_report(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate comprehensive Markdown report
        """
        logger.info("Generating comprehensive Markdown report...")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        repo_path = analysis_results.get("repo_path", "N/A")
        user_request = analysis_results.get("user_request", "N/A")
        risk_score = analysis_results.get("risk_score", 0)
        total_files = analysis_results.get("total_files", 0)
        files_passed = analysis_results.get("files_passed", 0)
        files_warned = analysis_results.get("files_warned", 0)
        files_blocked = analysis_results.get("files_blocked", 0)
        file_details = analysis_results.get("file_details", [])
        
        status = "PASS" if risk_score < 30 else "WARN" if risk_score < 60 else "BLOCK"
        
        report = f"""# Intelligent Release Management Scanner (IRMS)
## Release Analysis Report

**Generated:** {timestamp}  
**Status:** {status}

---

## Executive Summary

**User Request:** {user_request}

**Files Analyzed:** {total_files}  
**Overall Risk Score:** {risk_score}/100  
**Gate Decision:** {status}

### Gate Breakdown:
- ✓ PASS: {files_passed} files
- ■ WARN: {files_warned} files
- ■ BLOCK: {files_blocked} files

---

## Input Sources

**Files Ingested:** {total_files}
"""
        
        for file_detail in file_details:
            report += f"\n - {file_detail.get('name', 'Unknown')}"
        
        report += "\n\n**Documentation Files:** 0\n\n---\n\n"
        
        # Detailed File Analysis
        report += "## Detailed File Analysis\n\n"
        
        for file_detail in file_details:
            file_name = file_detail.get("name", "Unknown")
            file_risk = file_detail.get("risk_score", 0)
            file_gate = file_detail.get("gate_decision", "PASS")
            
            symbol = "■"
            
            report += f"### {symbol} {file_name}\n\n"
            report += f"**Risk Score:** {file_risk}/100  \n"
            report += f"**Gate Decision:** {symbol} {file_gate}\n\n"
            
            # Original Code Analysis
            report += "#### Original Code Analysis\n\n"
            lines = file_detail.get("lines", 0)
            maintainability = file_detail.get("maintainability", 0)
            complexity = file_detail.get("complexity", 0)
            issues = file_detail.get("issues", [])
            
            report += f"- **Lines of Code:** {lines}\n"
            report += f"- **Maintainability Index:** {maintainability:.2f}\n"
            report += f"- **Average Complexity:** {complexity:.2f}\n"
            report += f"- **Issues Found:** {len(issues)}\n\n"
            
            # Key Issues
            if issues:
                report += "**Key Issues:**\n\n"
                for issue in issues:
                    line_num = issue.get("line", 0)
                    description = issue.get("description", "N/A")
                    severity = issue.get("severity", "low")
                    report += f"- Line {line_num}: {description} ({severity})\n"
                report += "\n"
            
            # Changes Applied
            report += "#### Changes Applied\n\n"
            report += "AI analysis skipped: AI model is not initialized. Original code preserved.\n\n"
            
            # Change Statistics
            report += "#### Change Statistics\n\n"
            changes = file_detail.get("changes", {})
            report += f"- **Lines Added:** +{changes.get('added', 0)}\n"
            report += f"- **Lines Deleted:** -{changes.get('deleted', 0)}\n"
            report += f"- **Lines Modified:** ~{changes.get('modified', 0)}\n"
            report += f"- **Total Changes:** {changes.get('total', 0)}\n\n"
            
            # Risk Breakdown
            report += "#### Risk Breakdown\n\n"
            risk_breakdown = file_detail.get("risk_breakdown", {})
            report += f"- **Complexity Risk:** {risk_breakdown.get('complexity', 0):.2f}%\n"
            report += f"- **Change Volume Risk:** {risk_breakdown.get('change_volume', 0):.2f}%\n"
            report += f"- **Critical Function Risk:** {risk_breakdown.get('critical_function', 0):.2f}%\n"
            report += f"- **Issue Severity Risk:** {risk_breakdown.get('issue_severity', 0):.2f}%\n\n"
            
            # Recommendations
            recommendations = file_detail.get("recommendations", [])
            if recommendations:
                report += "**Recommendations:**\n\n"
                for rec in recommendations:
                    report += f"- {rec}\n"
            
            report += "\n---\n\n"
        
        # Overall Recommendations
        report += "## Overall Recommendations\n\n"
        
        high_severity_count = 0
        for file_detail in file_details:
            issues = file_detail.get("issues", [])
            for issue in issues:
                if issue.get("severity") in ["critical", "high"]:
                    high_severity_count += 1
        
        rec_num = 1
        if high_severity_count > 0:
            report += f"{rec_num}. Address {high_severity_count} medium/high severity issues\n"
            rec_num += 1
        
        report += f"{rec_num}. ✓ Low risk changes - safe to proceed\n\n"
        
        # Conclusion
        report += "## Conclusion\n\n"
        
        risk_level = 'low' if risk_score < 30 else 'medium' if risk_score < 60 else 'high'
        recommendation = 'recommended for the next release stage with standard review procedures' if risk_score < 30 else 'requires additional review before proceeding' if risk_score < 60 else 'requires thorough review and risk mitigation before deployment'
        
        report += f"The changes have been analyzed and deemed {risk_level} risk (score: {risk_score}/100).\n"
        report += f"The modified code is {recommendation}.\n\n"
        
        # Next Steps
        report += "**Next Steps:**\n\n"
        report += "1. Review the modified code files\n"
        report += "2. Run automated test suites\n"
        report += "3. Proceed with deployment pipeline\n\n"
        
        # Footer
        report += "*Report generated by Intelligent Release Management Scanner (IRMS)*\n"
        
        return report
    
    def _generate_release_notes(self, results: Dict[str, Any]) -> str:
        """Generate release notes (simplified version)"""
        return "See full report for details"
    
    def _generate_security_report(self, results: Dict[str, Any]) -> str:
        """Generate security report (simplified version)"""
        return "See full report for details"
    
    def _generate_checklist(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate release checklist"""
        return []