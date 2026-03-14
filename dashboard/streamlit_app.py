import streamlit as st
import os
import sys
import time

# Ensure the root directory is in the path for tool imports
sys.path.append(os.getcwd())

from agents.core import DigitalArcheologist
from tools.demo_utils import generate_broken_code
from tools.faiss_tool import ingest_code
from tools.docker_test_tool import run_isolated_test
from config import Config
from tools.github_tool import create_github_issue, get_github_issues, post_github_comment

# 1. Page Configuration
st.set_page_config(page_title="LogicFlow AI | Autonomous Agent", layout="wide")

# 2. State & Logs
if "logs" not in st.session_state:
    st.session_state.logs = "System Initialized: Polyglot Infrastructure Online."
if 'archeologist' not in st.session_state:
    st.session_state.archeologist = DigitalArcheologist()

def add_log(message):
    st.session_state.logs += f"\n[INFRA]: {message}"

# 3. Sidebar: Infrastructure & Agent Control
st.sidebar.title("giv Agent Control Center")

# Autonomous Mode Toggle
st.sidebar.markdown("---")
auto_mode = st.sidebar.toggle("Enable Autonomous Mode", help="When enabled, the agent will automatically solve the selected GitHub issue.")

# File Selection
st.sidebar.subheader(" Workspace Explorer")
available_files = [
    "demo/broken_code.py", 
    "demo/buggy.py", 
    "demo/logic.cpp", 
    "demo/utils.c", 
    "demo/app.js",
    "demo/utils.h"
]
target_file = st.sidebar.selectbox("Active Artifact", options=available_files)

# Bug Generator
if st.sidebar.button("Reset Excavation Site"):
    bug_type = generate_broken_code()
    with st.spinner("Re-indexing workspace..."):
        ingest_code()
    add_log(f"Injected new artifact: {bug_type}")
    st.rerun()

# Fetch active issues
issues = get_github_issues()

st.sidebar.markdown("---")
st.sidebar.subheader("Detected Corruption (GitHub)")

selected_issue_data = None
if isinstance(issues, list) and len(issues) > 0:
    issue_options = {f"#{i['number']}: {i['title']}": i for i in issues}
    selection = st.sidebar.selectbox("Active GitHub Issues", options=list(issue_options.keys()))
    selected_issue_data = issue_options[selection]
else:
    st.sidebar.info("No open issues found.")

# 4. Main UI Header
st.title("LogicFlow: Autonomous Polyglot Agent")
st.markdown("---")

col1, col2 = st.columns([1, 1])

# Column 1: Source Code View
with col1:
    st.header("Workspace View")
    st.info(f"Targeting: `{target_file}`")
    
    try:
        with open(target_file, "r") as f:
            code = f.read()
        ext = target_file.split('.')[-1]
        lang_style = 'cpp' if ext in ['cpp', 'c'] else 'python' if ext == 'py' else 'javascript'
        st.code(code, language=lang_style)
    except FileNotFoundError:
        st.warning(f"File {target_file} not found.")

# Column 2: Agent Activity & Autonomous Logic
with col2:
    st.header("Agent Activity")
    
    # Status Indicators for the "Agentic" feel
    if auto_mode:
        st.status(" Agent State: WATCHING REPOSITORY", state="running")
    else:
        st.status(" Agent State: STANDBY (Manual Mode)", state="complete")

    log_area = st.empty()
    log_area.code(st.session_state.logs, language="bash")

    st.markdown("---")
    
    if selected_issue_data:
        issue_num = selected_issue_data['number']
        issue_body = selected_issue_data.get('body', 'No description provided.')
        
        st.write(f"**Targeting Issue:** #{issue_num}")
        st.caption(f"Description: {issue_body[:80]}...")

        # TRIGGER LOGIC: Button click OR Auto-mode enabled
        repair_btn = st.button(f" Repair {target_file}")
        
        if repair_btn or auto_mode:
            if auto_mode:
                st.toast("Autonomous Triggered!", icon="")
                time.sleep(1) # Small delay for visual effect
            
            add_log(f"Archeologist Action: Solving Issue #{issue_num} in {target_file}")
            log_area.code(st.session_state.logs, language="bash")
            
            with st.spinner(f"Agent is excavating context and restoring {target_file}..."):
                result = st.session_state.archeologist.excavate_and_repair(
                    issue_id=issue_num, 
                    broken_code=code, 
                    file_name=target_file,
                    github_issue_text=issue_body
                )
                
                if result.get("success"):
                    st.balloons()
                    st.success(f"Repair Successful! Pull Request Created.")
                    
                    with st.expander(" View LogicFlow's Multi-Agent Review", expanded=True):
                        st.subheader("AI Reasoning")
                        st.info(result.get('explanation'))
                        
                        st.subheader(f" Senior Peer Review ({result.get('language')})")
                        st.success(result.get('review'))
                        
                        st.subheader("Docker Sandbox Logs")
                        st.code(result.get('test_log'), language="bash")
                        
                        if result.get('pr_url'):
                            st.link_button("View PR on GitHub", result['pr_url'])

                    # Final Comment Posting
                    fix_msg = f"Artifact Repaired! ({result.get('language')})\n\n**AI Reasoning:** {result.get('explanation')}\n\nFixed Code:\n```{ext}\n{result['restored_code']}\n```"
                    post_github_comment(issue_num, fix_msg)
                    add_log(f"Fix verified. Agent cycle complete.")
                else:
                    st.error(f"Stabilization failed.")
                    add_log(f"Error: Sandbox verification failed.")
                
                log_area.code(st.session_state.logs, language="bash")
                
                # Stop auto-mode after one successful cycle to prevent loops
                if auto_mode:
                    st.info("Autonomous task complete. Standing down.")
                    st.stop() 

    else:
        st.warning("Select a GitHub issue to begin.")

st.markdown("---")
st.caption("LogicFlow v3.0 (Autonomous) | Built by Dimply and Thrisha | Sahyadri College of Engineering")