import os
import argparse
import re
from dotenv import load_dotenv
import gitlab
from chatgpt_llm import ChatGPTLLM

# Load environments from .env
load_dotenv()

# Parse command-line arguments
parser = argparse.ArgumentParser(description="AI Code Review for GitLab MRs")
parser.add_argument("repository", help="Repository ID (project ID)")
parser.add_argument("mr_number", type=int, help="Merge Request number")
parser.add_argument("--mode", choices=["general", "issues", "comments"], default="general",
                    help="Mode: 'general' (MR overview), 'issues' (issues only), 'comments' (issues as MR comments)")
parser.add_argument("--full-context", action="store_true", default=False,
                    help="Send full files with diffs to OpenAI (default: diffs only)")
parser.add_argument("--debug", action="store_true", help="Print LLM API request details")
parser.add_argument("--gitlab-url", default="https://gitlab.com",
                    help="URL of your self-hosted GitLab instance (default: https://gitlab.com)")
args = parser.parse_args()

# Fetch GitLab token
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
if not GITLAB_TOKEN:
    raise ValueError("GITLAB_TOKEN environment variable is required")

# GitLab setup
gl = gitlab.Gitlab(args.gitlab_url, private_token=GITLAB_TOKEN)
project = gl.projects.get(args.repository)
mr = project.mergerequests.get(args.mr_number)

# LLM setup
llm = ChatGPTLLM(debug=args.debug)

# Function to parse diff and get file line number (for comments mode)
def get_file_line_from_diff(diff):
    lines = diff.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("@@"):
            match = re.match(r"@@ -(\d+),(\d+) \+(\d+),(\d+) @@", line)
            if match:
                new_start = int(match.group(3))  # Start line in the new file
                for j, diff_line in enumerate(lines[i+1:], start=1):
                    if diff_line.startswith("+") and not diff_line.startswith("+++"):
                        return new_start + j - 1  # Adjust for zero-based counting
    return 1  # Fallback if no valid line found


# Prepare content based on mode and full-context flag
if args.mode == "general":
    mr_title = mr.title or "No title provided"
    mr_description = mr.description or "No description provided"
    mr_author = mr.author['name']
    mr_web_url = mr.web_url
    if args.full_context:
        all_content = [f"MR Title: {mr_title}\nMR Description:\n{mr_description}"]
        for change in mr.changes()['changes']:
            if 'diff' in change:
                try:
                    file_content = project.files.get(file_path=change['new_path'], ref=mr.source_branch).decode().decode("utf-8")
                    all_content.append(f"File: {change['new_path']}\n{file_content}\n\nDiff:\n{change['diff']}\n{'-' * 16}")
                except Exception as e:
                    print(f"Error getting file content for {change['new_path']}: {str(e)}")
                    all_content.append(f"File: {change['new_path']}\n\nDiff:\n{change['diff']}\n{'-' * 16}")
        content = "\n\n".join(all_content)
    else:
        changes = [str(change) + "\n" + "-" * 16 for change in mr.changes()['changes'] if 'diff' in change]
        content = (f"MR Title: {mr_title}\n"
                    f"MR Author: {mr_author}\n"
                    f"MR Web URL: {mr_web_url}\n"
                    f"MR Description:\n{mr_description}\n\n"
                    f"Changes:\n") + "\n".join(changes)
elif args.mode in ["issues", "comments"]:
    if args.full_context:
        all_content = []
        for change in mr.changes()['changes']:
            if 'diff' in change:
                try:
                    file_content = project.files.get(file_path=change['new_path'], ref=mr.source_branch).decode().decode("utf-8")
                    all_content.append(f"File: {change['new_path']}\n{file_content}\n\nDiff:\n{change['diff']}\n{'-' * 16}")
                except Exception as e:
                    print(f"Error getting file content for {change['new_path']}: {str(e)}")
                    all_content.append(f"File: {change['new_path']}\n\nDiff:\n{change['diff']}\n{'-' * 16}")
        content = "\n\n".join(all_content)
    else:
        content = "\n".join([change['diff'] + "\n" + "-" * 16 for change in mr.changes()['changes'] if 'diff' in change])

# Get the review
review_text = llm.generate_review(content, args.mode)

# Process based on mode
if args.mode == "general":
    print(f"General MR Review:\n{review_text}")

elif args.mode == "issues":
    print(f"Code Issues:\n{review_text}")

elif args.mode == "comments":
    print(f"Code Issues:\n{review_text}")
    if mr.state == "opened":
        for change in mr.changes()['changes']:
            if 'diff' in change:
                try:
                    file_content = project.files.get(file_path=change['new_path'], ref=mr.source_branch).decode().decode("utf-8") if args.full_context else ""
                    diff = change['diff']
                    chunk = f"File: {change['new_path']}\n{file_content}\n\nDiff:\n{diff}" if args.full_context else diff
                    file_review = llm.generate_review(chunk, args.mode)

                    if file_review and "no feedback" not in file_review.lower():
                        line_num = get_file_line_from_diff(diff)
                        comment = f"AI Issue: {file_review}"
                        try:
                            mr.discussions.create({
                                'body': comment,
                                'position': {
                                    'base_sha': mr.diff_refs['base_sha'],
                                    'start_sha': mr.diff_refs['start_sha'],
                                    'head_sha': mr.diff_refs['head_sha'],
                                    'position_type': 'text',
                                    'new_path': change['new_path'],
                                    'new_line': line_num
                                }
                            })
                            print(f"Posted comment on {change['new_path']} at line {line_num}: {comment}")
                        except Exception as e:
                            print(f"Error posting comment on {change['new_path']}: {str(e)}")
                except Exception as e:
                    print(f"Error processing {change['new_path']}: {str(e)}")
    else:
        print("Comments mode: MR is closed, no comments posted.")
