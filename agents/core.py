import os
import logging
import json
import time
import streamlit as st
from google import genai
from google.genai import types
from config import Config
from tools.faiss_tool import retrieve_context
from tools.docker_test_tool import run_isolated_test
from tools.github_tool import create_pull_request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicFlow")

class DigitalArcheologist:
    def __init__(self):
        try:
            self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            logger.info("LogicFlow Final Evaluation Architect active.")
        except Exception as e:
            logger.error(f"Initialization failure: {e}")

    def excavate_and_repair(self, issue_id, broken_code, file_name="solution.py", github_issue_text=None):
        """
        Ultra-Resilient Engine with JSON-safe Feedback Loops.
        Ensures the Self-Correction loop never 'hangs' due to log formatting.
        """
        ext = file_name.split('.')[-1]
        lang_map = {'py': 'Python', 'js': 'JavaScript', 'cpp': 'C++', 'c': 'C', 'h': 'C/C++'}
        language = lang_map.get(ext, 'Python')

        # 1. ARCHAEOLOGICAL EXCAVATION
        search_query = f"{github_issue_text} {file_name} cross-file dependencies"
        context_snippets = retrieve_context(search_query, k=3) 
        context_str = "\n---\n".join([str(snippet) for snippet in context_snippets])

        current_attempt_code = broken_code
        attempts = 0
        max_attempts = 2
        feedback = "Initial analysis based on repository structure."

        while attempts < max_attempts:
            attempts += 1
            logger.info(f"Repair Attempt {attempts}/{max_attempts} for {file_name}")

            if attempts > 1:
                st.warning(f"Attempt 1 Failed. Self-Correcting...", icon="🤖")
                time.sleep(5) # Fast cooldown for live demo

            # 2. THE CONTEXTUAL PROMPT
            prompt = f"""
            ACT AS: Senior Software Architect.
            TASK: Fix the code and ensure multi-file consistency.
            
            RETURN ONLY JSON:
            {{
                "patches": {{"path": "code"}},
                "explanation": "text",
                "security_audit": "text",
                "is_secure": true
            }}

            CONTEXT: {context_str}
            FILE: {file_name}
            CODE: {current_attempt_code}
            COMPILER_FEEDBACK: {feedback}
            """

            try:
                # Using Gemini 3 Flash for speed and high context window
                model_name = "gemini-3-flash-preview" 
                
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                if not response.text:
                    raise ValueError("AI returned an empty response.")

                ai_data = json.loads(response.text)
                patches = ai_data.get('patches', {file_name: ai_data.get('code', '')})
                explanation = ai_data.get('explanation', 'Structural repair performed.')
                security_report = ai_data.get('security_audit', 'Audit passed.')
                
                primary_fix_code = patches.get(file_name, current_attempt_code)

                # 3. WORKSPACE SYNCHRONIZATION (Pre-emptive)
                for path, content in patches.items():
                    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
                    with open(path, "w") as f:
                        f.write(content)

                # 4. DOCKER VALIDATION
                success, test_log = run_isolated_test(primary_fix_code, file_name=file_name)
                
                if success:
                    # GITHUB PR CREATION
                    pr_url = create_pull_request(
                        issue_id=issue_id,
                        patches=patches,
                        explanation=f"LogicFlow verified fix.\n\n{explanation}\n\nSecurity: {security_report}"
                    )

                    return {
                        "success": True,
                        "restored_code": primary_fix_code,
                        "explanation": f"Fixed in {attempts} attempt(s).",
                        "review": security_report,
                        "test_log": test_log,
                        "pr_url": pr_url,
                        "files_fixed": list(patches.keys())
                    }
                else:
                    # CRITICAL: Sanitize the test_log before feeding it back
                    # This prevents quotes/newlines from breaking the next JSON prompt
                    clean_log = str(test_log).replace('"', "'").replace("\n", " ")
                    feedback = f"DOCKER_COMPILER_ERROR: {clean_log}"
                    current_attempt_code = primary_fix_code
                    logger.warning(f"Transitioning to Attempt 2. Error: {clean_log}")
                    
            except Exception as e:
                logger.error(f"LogicFlow Error: {e}")
                feedback = f"RUNTIME_EXCEPTION: {str(e)}"
                continue

        return {"success": False, "test_log": f"Failed after {max_attempts} attempts. Last Feedback: {feedback}"}