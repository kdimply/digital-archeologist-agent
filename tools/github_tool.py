import requests
from config import Config
import os
from github import Github
import logging

logger = logging.getLogger("LogicFlow.GitHub")

def create_pull_request(issue_id, fixed_code, file_path, explanation):
    """
    Advanced PR Creator: Commits multiple file changes (patches) 
    to a new branch and opens a Pull Request.
    """
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(os.getenv("REPO_NAME"))
    
    # Create a unique branch name
    branch_name = f"logicflow-fix-{issue_id}-{int(time.time())}"
    
    # Get the main branch SHA to start the new branch
    main_branch = repo.get_branch("main")
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)

    # Commit each file in the patches dictionary
    for file_path, content in patches.items():
        try:
            # Check if file exists to get its SHA for the update
            file_ref = repo.get_contents(file_path, ref=branch_name)
            repo.update_file(
                path=file_path, 
                message=f"LogicFlow: Synchronizing {file_path}", 
                content=content, 
                sha=file_ref.sha, 
                branch=branch_name
            )
        except Exception:
            # If file doesn't exist, create it
            repo.create_file(
                path=file_path, 
                message=f"LogicFlow: Initializing {file_path}", 
                content=content, 
                branch=branch_name
            )

    # Create the PR
    pr = repo.create_pull(
        title=f"LogicFlow Co-Repair: Issue #{issue_id}",
        body=explanation,
        base="main",
        head=branch_name
    )
    return pr.html_url

    
def get_github_issues():
    url = f"https://api.github.com/repos/{Config.GITHUB_REPO}/issues?state=open"
    headers = {
        "Authorization": f"token {Config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            issues_data = response.json()
            if not issues_data:
                return []
            # Returns a list of dicts for better UI handling
            return [{"number": i["number"], "title": i["title"]} for i in issues_data]
        else:
            return f"GitHub Error: {response.status_code}"
    except Exception as e:
        return f"Connection Error: {str(e)}"
    # Keep this for Dimply's Agent, but we'll use the function above for the Dashboard
def get_github_tools():
    # We will fix the agent's toolkit later if Dimply needs it, 
    # but for your dashboard, use get_github_issues()
    return []
def create_github_issue(title, body):
    """Creates a new issue in the repository."""
    url = f"https://api.github.com/repos/{Config.GITHUB_REPO}/issues"
    
    headers = {
        "Authorization": f"token {Config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {"title": title, "body": body}
    
   
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
            issue_data = response.json()
            return issue_data['number']  # Return the actual integer (e.g., 5)
    return None
    
def post_github_comment(issue_number, comment_body):
    """Posts a comment to a specific GitHub issue."""
    url = f"https://api.github.com/repos/{Config.GITHUB_REPO}/issues/{issue_number}/comments"
    
    headers = {
        "Authorization": f"token {Config.GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {"body": comment_body}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            return "✅ Comment posted successfully!"
        else:
            return f"❌ Failed to post comment: {response.status_code}"
    except Exception as e:
        return f"❌ Connection Error: {str(e)}"