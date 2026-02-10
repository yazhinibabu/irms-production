"""
IRMS Frontend - Enhanced Multi-Step Wizard UI
Production-ready interface with comprehensive features
"""

import streamlit as st
import requests
import json
from typing import Dict, Any, List, Optional
import time
import base64
from pathlib import Path
from datetime import datetime

# Backend API Configuration
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="IRMS - Intelligent Release Management Scanner",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #1a1d29;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
    }
    
    /* Step indicator */
    .step-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 30px 0;
        gap: 20px;
    }
    
    .step {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 18px;
    }
    
    .step-active {
        background: #4A90E2;
        color: white;
    }
    
    .step-inactive {
        background: #2d3142;
        color: #6c757d;
    }
    
    .step-complete {
        background: #4CAF50;
        color: white;
    }
    
    .step-arrow {
        color: #6c757d;
        font-size: 24px;
    }
    
    /* Input method cards */
    .input-card {
        background: #252a3a;
        border: 2px solid #3d4354;
        border-radius: 12px;
        padding: 30px;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
    }
    
    .input-card:hover {
        border-color: #4A90E2;
        transform: translateY(-5px);
    }
    
    .input-card-selected {
        border-color: #4A90E2;
        background: #2d3550;
    }
    
    /* Gate decision */
    .gate-pass {
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        color: white;
        font-size: 28px;
        font-weight: bold;
    }
    
    .gate-warn {
        background: linear-gradient(135deg, #F57C00 0%, #FF9800 100%);
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        color: white;
        font-size: 28px;
        font-weight: bold;
    }
    
    .gate-block {
        background: linear-gradient(135deg, #C62828 0%, #F44336 100%);
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        color: white;
        font-size: 28px;
        font-weight: bold;
    }
    
    /* File card */
    .file-card {
        background: #252a3a;
        border-left: 4px solid #4CAF50;
        padding: 20px;
        margin: 10px 0;
        border-radius: 8px;
    }
    
    .file-card-warn {
        border-left-color: #FF9800;
    }
    
    .file-card-block {
        border-left-color: #F44336;
    }
    
    /* Metrics */
    .metric-card {
        background: #252a3a;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 36px;
        font-weight: bold;
        color: #4CAF50;
    }
    
    /* Tips box */
    .tips-box {
        background: #e3f2fd;
        border-left: 4px solid #2196F3;
        padding: 15px;
        margin: 20px 0;
        border-radius: 4px;
        color: #0d47a1;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'input_method' not in st.session_state:
    st.session_state.input_method = None
if 'repo_path' not in st.session_state:
    st.session_state.repo_path = ""
if 'user_request' not in st.session_state:
    st.session_state.user_request = ""
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []

def check_backend_health() -> bool:
    """Check if backend is available"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def analyze_repository(repo_path: str, user_request: str, enable_ai: bool) -> Optional[Dict[str, Any]]:
    """Send analysis request to backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/analyze",
            json={
                "repo_path": repo_path,
                "user_request": user_request,
                "enable_ai": enable_ai
            },
            timeout=300
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Backend error: {str(e)}")
        return None

def display_step_indicator():
    """Display step progress indicator"""
    current = st.session_state.current_step
    
    steps = [
        ("1", "Select Input"),
        ("2", "Describe Changes"),
        ("3", "Run Analysis")
    ]
    
    html = '<div class="step-container">'
    
    for i, (num, label) in enumerate(steps):
        step_num = i + 1
        
        if step_num < current:
            circle_class = "step-circle step-complete"
        elif step_num == current:
            circle_class = "step-circle step-active"
        else:
            circle_class = "step-circle step-inactive"
        
        html += f'''
        <div class="step">
            <div class="{circle_class}">{num}</div>
            <span style="color: {"#4A90E2" if step_num == current else "#6c757d"}; font-weight: bold;">{label}</span>
        </div>
        '''
        
        if i < len(steps) - 1:
            html += '<div class="step-arrow">→</div>'
    
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)

def step1_select_input():
    """Step 1: Select Input Method"""
    st.markdown("## 📁 Step 1: Select Input Method")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_local = st.session_state.input_method == "local"
        card_class = "input-card input-card-selected" if selected_local else "input-card"
        
        if st.button("🔍 Scan Local Project\nScan entire project directory", key="btn_local", use_container_width=True):
            st.session_state.input_method = "local"
            st.rerun()
    
    with col2:
        selected_upload = st.session_state.input_method == "upload"
        card_class = "input-card input-card-selected" if selected_upload else "input-card"
        
        if st.button("📤 Upload Files\nUpload specific files manually", key="btn_upload", use_container_width=True):
            st.session_state.input_method = "upload"
            st.rerun()
    
    st.markdown("---")
    
    # Show input based on selection
    if st.session_state.input_method == "local":
        st.markdown("### 🔍 Scan Project Directory")
        st.markdown("*Recursively scan a project for source code files*")
        
        repo_path = st.text_input(
            "Project Path",
            value=st.session_state.repo_path,
            placeholder=".",
            help="Enter project directory path"
        )
        
        st.session_state.repo_path = repo_path
        
        # Tips
        st.markdown("""
        <div class="tips-box">
            <strong>💡 Tips</strong><br>
            • Use "." to scan the current directory<br>
            • Supports recursive scanning with .gitignore respect<br>
            • Automatically detects supported file types
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Scan Project", type="primary", use_container_width=True):
            if repo_path:
                st.session_state.current_step = 2
                st.rerun()
            else:
                st.error("Please enter a project path")
    
    elif st.session_state.input_method == "upload":
        st.markdown("### 📤 Upload Files")
        st.markdown("*Upload specific files manually*")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            type=['py', 'js', 'java', 'c', 'cpp', 'h', 'hpp', 'cs', 'go', 'rs']
        )
        
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
            
            for file in uploaded_files:
                st.write(f"- {file.name}")
            
            if st.button("Continue →", type="primary", use_container_width=True):
                st.session_state.current_step = 2
                st.rerun()

def step2_describe_changes():
    """Step 2: Describe Changes"""
    st.markdown("## 📝 Step 2: Describe Changes")
    
    st.markdown("*Describe what changes you want to make or analyze*")
    
    user_request = st.text_area(
        "User Request",
        value=st.session_state.user_request,
        placeholder="Example: Add comprehensive error handling, type hints, docstrings, and logging to all functions",
        height=150,
        help="Describe the changes or analysis you want to perform"
    )
    
    st.session_state.user_request = user_request
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        if st.button("Continue →", type="primary", use_container_width=True):
            if user_request:
                st.session_state.current_step = 3
                st.rerun()
            else:
                st.error("Please describe the changes")

def step3_run_analysis():
    """Step 3: Run Analysis"""
    st.markdown("## 🚀 Step 3: Run Analysis")
    
    if st.session_state.analysis_results is None:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.current_step = 2
                st.rerun()
        
        with col2:
            if st.button("▶ Run IRMS Analysis", type="primary", use_container_width=True):
                run_analysis()
    else:
        display_results()

def run_analysis():
    """Execute the analysis"""
    with st.spinner("🔄 Analyzing... This may take a few minutes."):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.02)
            progress_bar.progress(i + 1)

        enable_ai = st.session_state.get("enable_ai", False)

        # Upload-based analysis
        if st.session_state.input_method == "upload" and st.session_state.uploaded_files:
            files_data = [
                ("files", (f.name, f.getvalue(), f.type))
                for f in st.session_state.uploaded_files
            ]

            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/analyze-files",
                    files=files_data,
                    data={
                        "user_request": st.session_state.user_request,
                        "enable_ai": enable_ai,
                    },
                    timeout=300,
                )
                response.raise_for_status()
                results = response.json()
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                return

        # Directory-based analysis
        else:
            results = analyze_repository(
                st.session_state.repo_path,
                st.session_state.user_request,
                enable_ai,
            )

        if results:
            st.session_state.analysis_results = results
            st.rerun()

def display_results():
    """Display comprehensive analysis results"""
    results = st.session_state.analysis_results
    
    st.markdown('<div class="success-box" style="background-color: #1E4620; border: 1px solid #2E7D32; border-radius: 8px; padding: 20px; color: #4CAF50; font-size: 18px; font-weight: bold; margin: 20px 0;">✅ Analysis complete!</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Overall Results
    st.markdown("## 📊 Overall Results")
    
    risk_score = results.get("risk_score", 0)
    total_files = results.get("total_files", 0)
    files_passed = results.get("files_passed", 0)
    files_warned = results.get("files_warned", 0)
    files_blocked = results.get("files_blocked", 0)
    
    gate_decision, gate_class, gate_icon = get_gate_decision(risk_score)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### Gate Decision")
        st.markdown(f'<div class="{gate_class}">{gate_icon} {gate_decision}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Risk Score")
        st.markdown(f"""
        <div style="text-align: center; padding: 30px;">
            <div style="font-size: 72px; font-weight: bold; color: #FFFFFF;">{risk_score}/100</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("### Files Analyzed")
        st.metric("", total_files)
    
    with col4:
        st.markdown("### Gate Breakdown")
        st.write(f"✅ PASS: {files_passed}")
        st.write(f"⚠️ WARN: {files_warned}")
        st.write(f"🔴 BLOCK: {files_blocked}")
    
    st.markdown("---")
    
    # Change Summary
    display_change_summary(results)
    
    st.markdown("---")
    
    # File-by-File Details
    display_file_details_comprehensive(results)
    
    st.markdown("---")
    
    # Downloads
    display_downloads_enhanced(results)
    
    # Reset button
    if st.button("🔄 Start New Analysis", type="primary"):
        st.session_state.current_step = 1
        st.session_state.analysis_results = None
        st.session_state.input_method = None
        st.rerun()

def get_gate_decision(risk_score: float) -> tuple:
    """Determine gate decision based on risk score"""
    if risk_score < 30:
        return "PASS", "gate-pass", "✅"
    elif risk_score < 60:
        return "WARN", "gate-warn", "⚠️"
    else:
        return "BLOCK", "gate-block", "🔴"

def display_change_summary(results: Dict[str, Any]):
    """Display change summary"""
    st.markdown("## 📝 Change Summary")
    
    changes = results.get("changes", {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #888;">Lines Added</div>
            <div class="metric-value" style="color: #4CAF50;">+{changes.get("lines_added", 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #888;">Lines Deleted</div>
            <div class="metric-value" style="color: #F44336;">-{changes.get("lines_deleted", 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #888;">Lines Modified</div>
            <div class="metric-value" style="color: #FF9800;">~{changes.get("lines_modified", 0)}</div>
        </div>
        """, unsafe_allow_html=True)

def display_file_details_comprehensive(results: Dict[str, Any]):
    """Display comprehensive file-by-file analysis"""
    st.markdown("## 📄 File-by-File Details")
    
    files = results.get("file_details", [])
    
    if not files:
        st.info("No file details available")
        return
    
    for file_info in files:
        status = file_info.get("gate_decision", "PASS")
        risk = file_info.get("risk_score", 0)
        
        # Determine card styling
        if status == "PASS":
            icon = "✅"
            card_class = "file-card"
        elif status == "WARN":
            icon = "⚠️"
            card_class = "file-card file-card-warn"
        else:
            icon = "🔴"
            card_class = "file-card file-card-block"
        
        with st.expander(f"{icon} {file_info.get('name', 'Unknown')} - {status} (Risk: {risk}/100)"):
            # Original Code Analysis
            st.markdown("#### Original Code Analysis")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Lines of Code", file_info.get("lines", 0))
            with col2:
                st.metric("Maintainability Index", f"{file_info.get('maintainability', 0):.2f}")
            with col3:
                st.metric("Average Complexity", f"{file_info.get('complexity', 0):.2f}")
            
            # Issues
            issues = file_info.get("issues", [])
            if issues:
                st.markdown("**Key Issues:**")
                for issue in issues:
                    severity = issue.get("severity", "low")
                    severity_icon = "🔴" if severity == "critical" else "🟠" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                    st.write(f"{severity_icon} Line {issue.get('line', 0)}: {issue.get('description', 'N/A')} ({severity})")
            
            # Change Statistics
            st.markdown("#### Change Statistics")
            changes = file_info.get("changes", {})
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write(f"**Lines Added:** +{changes.get('added', 0)}")
            with col2:
                st.write(f"**Lines Deleted:** -{changes.get('deleted', 0)}")
            with col3:
                st.write(f"**Lines Modified:** ~{changes.get('modified', 0)}")
            with col4:
                st.write(f"**Total Changes:** {changes.get('total', 0)}")
            
            # Risk Breakdown
            st.markdown("#### Risk Breakdown")
            risk_breakdown = file_info.get("risk_breakdown", {})
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"• Complexity Risk: {risk_breakdown.get('complexity', 0):.1f}%")
                st.write(f"• Change Volume Risk: {risk_breakdown.get('change_volume', 0):.1f}%")
            with col2:
                st.write(f"• Critical Function Risk: {risk_breakdown.get('critical_function', 0):.1f}%")
                st.write(f"• Issue Severity Risk: {risk_breakdown.get('issue_severity', 0):.1f}%")
            
            # Recommendations
            recommendations = file_info.get("recommendations", [])
            if recommendations:
                st.markdown("**Recommendations:**")
                for rec in recommendations:
                    st.write(f"• {rec}")

def display_downloads_enhanced(results: Dict[str, Any]):
    """Enhanced downloads section"""
    st.markdown("## ⬇️ Downloads")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Modified Code")
        
        files = results.get("file_details", [])
        if files:
            for idx, file_info in enumerate(files):
                file_name = file_info.get("name", f"file_{idx}.txt")
                
                # Generate modified content
                modified_content = file_info.get("modified_code", f"# Modified: {file_name}\n# Changes applied\n")
                
                st.download_button(
                    label=f"💾 Download {file_name}",
                    data=modified_content.encode() if isinstance(modified_content, str) else modified_content,
                    file_name=file_name,
                    mime="text/plain",
                    key=f"download_file_{idx}"
                )
        else:
            st.info("No modified files available")
    
    with col2:
        st.markdown("### Report")
        
        # Markdown Report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report_md = generate_markdown_report(results)
        st.download_button(
            label="📥 Download Report (Markdown)",
            data=report_md.encode(),
            file_name=f"IRMS_Report_{timestamp}.md",
            mime="text/markdown",
            key="download_md"
        )
        
        # PDF Report
        if st.button("📄 Generate PDF Report", key="gen_pdf"):
            with st.spinner("Generating PDF..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/generate-report",
                        json={
                            "results": results,
                            "format": "pdf"
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        pdf_content = response.content
                        st.download_button(
                            label="💾 Download Report.pdf",
                            data=pdf_content,
                            file_name=f"IRMS_Report_{timestamp}.pdf",
                            mime="application/pdf",
                            key="download_pdf"
                        )
                        st.success("✅ PDF generated!")
                    else:
                        st.error("Failed to generate PDF")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def generate_markdown_report(results: Dict[str, Any]) -> str:
    """Generate comprehensive markdown report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    risk_score = results.get("risk_score", 0)
    gate_decision = "PASS" if risk_score < 30 else "WARN" if risk_score < 60 else "BLOCK"
    
    report = f"""# IRMS Analysis Report

**Generated:** {timestamp}
**Status:** {gate_decision}

## Executive Summary

**User Request:** {results.get('user_request', 'N/A')}

**Files Analyzed:** {results.get('total_files', 0)}
**Overall Risk Score:** {risk_score}/100
**Gate Decision:** {gate_decision}

### Gate Breakdown:
- ✅ PASS: {results.get('files_passed', 0)} files
- ⚠️ WARN: {results.get('files_warned', 0)} files
- 🔴 BLOCK: {results.get('files_blocked', 0)} files

## Detailed File Analysis

"""
    
    for file_info in results.get("file_details", []):
        report += f"""
### {file_info.get('name', 'Unknown')}

**Risk Score:** {file_info.get('risk_score', 0)}/100
**Gate Decision:** {file_info.get('gate_decision', 'PASS')}

#### Original Code Analysis
- **Lines of Code:** {file_info.get('lines', 0)}
- **Maintainability Index:** {file_info.get('maintainability', 0):.2f}
- **Average Complexity:** {file_info.get('complexity', 0):.2f}
- **Issues Found:** {len(file_info.get('issues', []))}

"""
        
        issues = file_info.get("issues", [])
        if issues:
            report += "**Key Issues:**\n"
            for issue in issues:
                report += f"- Line {issue.get('line', 0)}: {issue.get('description', 'N/A')} ({issue.get('severity', 'low')})\n"
        
        report += "\n"
    
    report += """
## Overall Recommendations

1. Review all high/critical severity issues
2. Run automated test suites
3. Proceed with deployment pipeline

*Report generated by IRMS - Intelligent Release Management Scanner*
"""
    
    return report

def main():
    st.title("🔍 Intelligent Release Management Scanner (IRMS)")
    st.markdown("---")
    
    # Check backend health
    if not check_backend_health():
        st.error("⚠️ Backend is not running! Please start the backend server first.")
        st.info("Run: `cd backend && python main.py`")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        enable_ai = st.checkbox(
            "Enable AI Analysis",
            value=False,
            help="Use Gemini 2.5 Flash for enhanced insights"
        )
        st.session_state.enable_ai = enable_ai
        
        if enable_ai:
            st.success("✨ AI-powered insights enabled")
        
        st.divider()
        
        st.header("📋 About")
        st.markdown("""
        **IRMS** analyzes your codebase for:
        - ✅ Code structure & dependencies
        - 🔐 Security vulnerabilities
        - 📊 Change detection
        - ⚠️ Risk assessment
        - 📄 Automated documentation
        - 🚦 CI/CD gate decisions
        """)
    
    # Step indicator
    display_step_indicator()
    
    # Display current step
    if st.session_state.current_step == 1:
        step1_select_input()
    elif st.session_state.current_step == 2:
        step2_describe_changes()
    elif st.session_state.current_step == 3:
        step3_run_analysis()

if __name__ == "__main__":
    main()