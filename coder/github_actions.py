from claude_code_sdk import tool
from github import Github
import json
import os
from pathlib import Path

# Load .env file if it exists
env_file = Path(".env")
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                # Remove quotes if present
                value = value.strip('"').strip("'")
                os.environ[key] = value

# Initialize API with authentication
# Use GITHUB_TOKEN environment variable if available
github_token = os.environ.get("GITHUB_TOKEN")
if github_token:
    print(f"Using GitHub token (first 4 chars): {github_token[:4]}...")
    from github import Auth

    auth = Auth.Token(github_token)
    g = Github(auth=auth)
else:
    print("No GitHub token found, using unauthenticated access")
    g = Github()


# Get issue data
@tool(
    "Get Issue Data",
    "Fetch detailed information about a GitHub issue, including comments, events, and labels.",
    {"owner": str, "repo": str, "issue_number": str},
)
def get_issue_data(owner, repo, issue_number):
    repo_obj = g.get_repo(f"{owner}/{repo}")
    issue = repo_obj.get_issue(issue_number)

    # Get comments
    comments = list(issue.get_comments())

    # Get events (timeline)
    events = list(issue.get_events())

    # Get labels
    labels = list(issue.get_labels())

    return {
        "issue": {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "state": issue.state,
            "user": issue.user.login,
            "assignees": [a.login for a in issue.assignees],
            "labels": [label.name for label in labels],
            "milestone": issue.milestone.title if issue.milestone else None,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "closed_at": issue.closed_at,
            "url": issue.html_url,
            "id": issue.id,
        },
        "comments": [
            {
                "id": c.id,
                "user": c.user.login,
                "body": c.body,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            }
            for c in comments
        ],
        "events": [
            {
                "event": e.event,
                "actor": e.actor.login if e.actor else None,
                "created_at": e.created_at,
                "commit_id": e.commit_id,
            }
            for e in events
        ],
    }


# Get PR data
def get_pr_data(owner, repo, pull_number):
    repo_obj = g.get_repo(f"{owner}/{repo}")
    pr = repo_obj.get_pull(pull_number)

    # Get PR reviews
    reviews = list(pr.get_reviews())

    # Get PR review comments
    review_comments = list(pr.get_review_comments())

    # Get PR commits
    commits = list(pr.get_commits())

    # Get files changed
    files = list(pr.get_files())

    # Get general comments (issue comments)
    comments = list(pr.get_issue_comments())

    return {
        "pr": {
            "number": pr.number,
            "title": pr.title,
            "body": pr.body,
            "state": pr.state,
            "user": pr.user.login,
            "assignees": [a.login for a in pr.assignees],
            "labels": [label.name for label in pr.labels],
            "milestone": pr.milestone.title if pr.milestone else None,
            "created_at": pr.created_at,
            "updated_at": pr.updated_at,
            "closed_at": pr.closed_at,
            "merged_at": pr.merged_at,
            "merge_commit_sha": pr.merge_commit_sha,
            "head": {
                "ref": pr.head.ref,
                "sha": pr.head.sha,
                "repo": pr.head.repo.full_name if pr.head.repo else None,
            },
            "base": {
                "ref": pr.base.ref,
                "sha": pr.base.sha,
                "repo": pr.base.repo.full_name,
            },
            "mergeable": pr.mergeable,
            "mergeable_state": pr.mergeable_state,
            "merged": pr.merged,
            "merged_by": pr.merged_by.login if pr.merged_by else None,
            "url": pr.html_url,
            "id": pr.id,
            "additions": pr.additions,
            "deletions": pr.deletions,
            "changed_files": pr.changed_files,
        },
        "reviews": [
            {
                "id": r.id,
                "user": r.user.login,
                "body": r.body,
                "state": r.state,
                "submitted_at": r.submitted_at,
                "commit_id": r.commit_id,
            }
            for r in reviews
        ],
        "review_comments": [
            {
                "id": rc.id,
                "user": rc.user.login,
                "body": rc.body,
                "path": rc.path,
                "position": rc.position,
                "line": rc.line,
                "commit_id": rc.commit_id,
                "created_at": rc.created_at,
                "updated_at": rc.updated_at,
            }
            for rc in review_comments
        ],
        "commits": [
            {
                "sha": c.sha,
                "author": c.commit.author.name,
                "message": c.commit.message,
                "date": c.commit.author.date,
                "url": c.html_url,
            }
            for c in commits
        ],
        "files": [
            {
                "filename": f.filename,
                "status": f.status,
                "additions": f.additions,
                "deletions": f.deletions,
                "changes": f.changes,
                "patch": f.patch if hasattr(f, "patch") else None,
            }
            for f in files
        ],
        "comments": [
            {
                "id": c.id,
                "user": c.user.login,
                "body": c.body,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
            }
            for c in comments
        ],
    }


# Utility functions
def get_all_issues(owner, repo, state="all"):
    """Get all issues from a repository"""
    repo_obj = g.get_repo(f"{owner}/{repo}")
    issues = repo_obj.get_issues(state=state)

    return [
        {
            "number": issue.number,
            "title": issue.title,
            "state": issue.state,
            "user": issue.user.login,
            "created_at": issue.created_at,
            "updated_at": issue.updated_at,
            "labels": [label.name for label in issue.labels],
            "is_pr": issue.pull_request is not None,
        }
        for issue in issues
    ]


def get_all_prs(owner, repo, state="all"):
    """Get all pull requests from a repository"""
    repo_obj = g.get_repo(f"{owner}/{repo}")
    prs = repo_obj.get_pulls(state=state)

    return [
        {
            "number": pr.number,
            "title": pr.title,
            "state": pr.state,
            "user": pr.user.login,
            "created_at": pr.created_at,
            "updated_at": pr.updated_at,
            "merged": pr.merged,
            "head_ref": pr.head.ref,
            "base_ref": pr.base.ref,
        }
        for pr in prs
    ]


if __name__ == "__main__":
    owner = "himmelreich-it"
    repo = "scan-receipts"
    issue_number = 21  # Replace with your issue number (must be integer)

    try:
        data = get_issue_data(owner, repo, issue_number)
        # Print or process the data as needed
        print(json.dumps(data, indent=2, default=str))
    except Exception as e:
        print(f"Error: {e}")
        print(
            "\nIf this is a private repository, please set GITHUB_TOKEN environment variable:"
        )
        print("export GITHUB_TOKEN=your_github_personal_access_token")
