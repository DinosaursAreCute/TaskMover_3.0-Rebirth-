import os
import re
import requests

REPO = os.environ["GITHUB_REPOSITORY"]
API_URL = f"https://api.github.com/repos/{REPO}/issues"
TOKEN = os.environ["GITHUB_TOKEN"]
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github+json"}

for root, _, files in os.walk("docs/Architechture"):
    for file in files:
        if file.endswith(".md"):
            with open(os.path.join(root, file), encoding="utf-8") as f:
                content = f.read()
                # Find all checklist items
                for match in re.finditer(r"\- \[ \] (.+)", content):
                    title = match.group(1).strip()
                    body = f"Checklist item from `{file}`:\n\n{title}"
                    # Optionally, avoid duplicates by searching existing issues here
                    data = {"title": title, "body": body}
                    r = requests.post(API_URL, json=data, headers=HEADERS)
                    print(f"Issue created: {r.json().get('html_url', r.text)}")
