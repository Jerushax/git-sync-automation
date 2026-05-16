# Automatic Cross-Repository File Sync with Merge Request Creation

## Project Overview

This project automatically syncs files from one GitLab repository (Repo A) to another repository (Repo B) whenever a merge happens.

The system listens for GitLab webhook events, detects changed files, copies them to the target repository, creates a new branch, pushes the code, and automatically creates a Merge Request.

### Workflow

```text
Repo A Merge
↓
Webhook triggers app
↓
Detect changed files
↓
Copy files to Repo B
↓
Create branch
↓
Push code
↓
Create Merge Request automatically
```

---

# Features

- Detects GitLab merge events automatically
- Syncs only changed files
- Preserves folder structure
- Creates sync branch automatically
- Pushes code to Repo B
- Creates Merge Request automatically
- Supports excluded paths
- Prevents unwanted overwrites
- Logging support included

---

# Prerequisites

Before running the project, install the following:

## Required Software

- Python 3.10+
- Git
- GitLab Account
- ngrok Account

## Required Access

You need:

- GitLab Personal Access Token
- Access to both repositories

---

# Project Structure

```text
repo-sync-automation/
│
├── src/
│   ├── main.py
│   ├── git_manager.py
│   ├── sync_engine.py
│   ├── webhook_handler.py
│   ├── mr_creator.py
│   ├── conflict_handler.py
│   ├── logger.py
│   └── config_loader.py
│
├── config/
│   └── config.yaml
│
├── tests/
│
├── logs/
│
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── .env
```

---

# Clone the Repository

```bash
git clone <repo-url>
cd repo-sync-automation
```

---

# Create Virtual Environment

You can use:

- CMD
- PowerShell
- VS Code Terminal

## Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# Install Requirements

```bash
pip install -r requirements.txt
```

---

# Environment Variables Setup

Create a file named `.env` in the project root folder.

Example:

```env
GITLAB_TOKEN=your_gitlab_token
WEBHOOK_SECRET=your_webhook_secret
```

## How to Generate GitLab Token

1. Open GitLab
2. Go to:

```text
Profile → Preferences → Access Tokens
```

3. Create token with permissions:

- api
- read_repository
- write_repository

4. Copy the token
5. Paste it inside `.env`

---

# Configure config.yaml

Open:

```text
config/config.yaml
```

Example configuration:

```yaml
app:
  host: 0.0.0.0
  port: 8000

source_repo:
  name: repo-a
  url: https://gitlab.com/username/repo-a.git
  branch: main

target_repo:
  name: repo-b
  url: https://gitlab.com/username/repo-b.git
  branch: main

sync:
  working_dir: repos
  sync_branch_prefix: sync

  excluded_paths:
    - .git/
    - node_modules/
    - __pycache__/
    - docs/

merge_request:
  target_branch: main
  title_prefix: "Auto Sync"

logging:
  file: logs/app.log
```

---

# Run the Application

Open terminal inside the project folder.

Run:

```bash
python src/main.py
```

If using FastAPI + Uvicorn:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

# ngrok Setup

## Why ngrok is Needed

GitLab webhooks cannot access:

```text
localhost:8000
```

ngrok creates a public URL that forwards requests to your local machine.

---

## Step 1 — Download ngrok

Download from:

```text
https://ngrok.com/
```

---

## Step 2 — Create Account

- Sign up
- Login
- Copy your auth token

---

## Step 3 — Authenticate ngrok

```bash
ngrok config add-authtoken YOUR_TOKEN
```

---

## Step 4 — Start Tunnel

```bash
ngrok http 8000
```

You will get a URL like:

```text
https://abc123.ngrok-free.app
```

Webhook URL:

```text
https://abc123.ngrok-free.app/webhook
```

Copy this URL.

---

# GitLab Webhook Setup

## Steps

### 1. Open Repo A

Go to:

```text
Settings → Webhooks
```

### 2. Paste ngrok URL

Example:

```text
https://abc123.ngrok-free.app/webhook
```

### 3. Select Trigger

Enable:

- Merge Request Events

### 4. Save Webhook

Click:

```text
Add Webhook
```

---

# How to Get Project ID of Repo B

## Method 1 — GitLab UI

Open Repo B.

On the project homepage, look at the right sidebar.

You will see:

```text
Project ID: 12345678
```

Copy this ID.

---

## Method 2 — GitLab API

```bash
curl --header "PRIVATE-TOKEN: <token>" \
https://gitlab.com/api/v4/projects
```

---

## Where to Use Project ID

Paste the Project ID inside:

- `.env`
- `config.yaml`
- or wherever your MR API logic uses it

---

# How the Workflow Works

## Step-by-Step Flow

### 1. Merge happens in Repo A

Developer merges code into main branch.

↓

### 2. GitLab webhook triggers Python app

GitLab sends webhook payload.

↓

### 3. Changed files detected

Application compares commits.

↓

### 4. Files copied to Repo B

Only modified files are synced.

↓

### 5. New branch created

Example:

```text
sync/20260515
```

↓

### 6. Commit pushed

Application pushes changes automatically.

↓

### 7. Merge Request created

MR gets created using GitLab API.

---

# Core Modules Explanation

## main.py

Creates FastAPI server.

```python
app = FastAPI()
```

Webhook endpoint:

```python
@app.post("/webhook")
```

GitLab sends webhook events here.

---

## git_manager.py

Handles Git operations.

### Responsibilities

- Clone repository
- Pull latest code
- Create branch
- Commit changes
- Push branch

Example logic:

```python
if repo exists:
    git pull
else:
    git clone
```

### create_branch()

Creates branch like:

```text
sync/20260515
```

### commit_changes()

Runs:

```bash
git add .
git commit
```

### push_branch()

Runs:

```bash
git push
```

GitPython allows Python to control Git.

---

## sync_engine.py

Responsible for file synchronization.

### Responsibilities

- Copy modified files
- Delete removed files
- Preserve folder structure

### Git Status Types

| Status | Meaning |
|---|---|
| A | Added |
| M | Modified |
| D | Deleted |

Example:

```python
('M', 'hello.txt')
```

Means:

```text
Modified file
```

Uses:

```bash
git diff old_commit new_commit
```

For comparing commits.

Uses:

```python
shutil.copy2()
```

To preserve:

- file content
- metadata

---

## mr_creator.py

Creates Merge Request automatically using GitLab API.

Without API:

- Manual MR creation needed

### create_merge_request()

Sends HTTP POST request:

```json
{
  "source_branch": "sync/123",
  "target_branch": "main",
  "title": "Auto Sync"
}
```

---

## conflict_handler.py

Prevents overwriting files blindly.

Scenario:

- Repo B already changed same file

Automation should avoid overwriting directly.

---

# Merge Detection Improvement

Initial approach:

```text
Webhook SHA payload
```

Can sometimes be inconsistent.

Better approach:

```text
Local HEAD comparison
```

OR

```text
GitLab Merge Request Changes API
```

Comparison Table:

| Method | Reliability |
|---|---|
| Webhook SHA payload | Inconsistent |
| Local HEAD comparison | Stable |

---

# Example Run

Example terminal logs:

```text
[INFO] Webhook received
[INFO] Cloning source repository
[INFO] Detecting changed files
[INFO] Copying updated files
[INFO] Creating sync branch
[INFO] Committing changes
[INFO] Pushing branch
[INFO] Creating Merge Request
[INFO] Sync completed successfully
```

---

# Troubleshooting

## ngrok URL not working

### Fix

- Ensure ngrok is running
- Verify correct port

Example:

```bash
ngrok http 8000
```

---

## Invalid GitLab Token

### Fix

Verify token permissions:

- api
- read_repository
- write_repository

---

## Webhook not triggering

### Fix

Check:

```text
GitLab → Settings → Webhooks
```

Verify:

- Correct URL
- Merge Request Events enabled

---

## Git Permission Denied

### Fix

Reconfigure Git credentials.

Check:

```bash
git config --global user.name
git config --global user.email
```

---

## Merge Request not creating

### Fix

Check:

- Project ID
- Token permissions
- API endpoint

---

# Useful Commands

## Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

---

## Install Requirements

```bash
pip install -r requirements.txt
```

---

## Run Application

```bash
python src/main.py
```

---

## Run FastAPI with Uvicorn

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

---

## Start ngrok

```bash
ngrok http 8000
```

---

# Future Improvements

- Docker deployment
- Kubernetes support
- Multiple repo sync support
- Better conflict resolution
- UI dashboard
- Retry queue system
- Slack notifications

---

# Author

Developed for automated GitLab repository synchronization and Merge Request creation.

Designed for DevOps automation, CI/CD workflows, and repository management.
