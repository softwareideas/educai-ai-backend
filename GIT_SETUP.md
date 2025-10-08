# 🚀 Git Setup & GitHub Push Guide

## Prerequisites

1. Git installed on your system
2. GitHub account created
3. Git configured with your credentials

## Step 1: Configure Git (First Time Only)

```bash
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

## Step 2: Initialize Local Repository

```bash
# Navigate to your project directory (if not already there)
cd /Users/danussh/Desktop/educa-ai-backend

# Initialize git repository
git init

# Add all files to staging area
git add .

# Create your first commit
git commit -m "Initial commit: World-Class Medical Learning AI Backend"
```

## Step 3: Create GitHub Repository

### Option A: Using GitHub Website

1. Go to [https://github.com](https://github.com)
2. Click the **"+"** icon in the top right → **"New repository"**
3. Fill in the details:
   - **Repository name**: `educa-ai-backend` (or your preferred name)
   - **Description**: "World-Class Medical Learning AI - NEET Preparation Platform with RAG, Multi-Agent System, and Advanced Teaching Modes"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README (you already have one)
   - **DO NOT** add .gitignore (you already have one)
4. Click **"Create repository"**

### Option B: Using GitHub CLI (if installed)

```bash
# Install GitHub CLI first (if not installed)
# macOS: brew install gh

# Login to GitHub
gh auth login

# Create repository
gh repo create educa-ai-backend --public --source=. --remote=origin --push
```

## Step 4: Connect Local Repository to GitHub

After creating the repository on GitHub, you'll see instructions. Use these commands:

```bash
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/educa-ai-backend.git

# Verify remote was added
git remote -v

# Push your code to GitHub
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

## Step 5: Verify Upload

1. Go to `https://github.com/YOUR_USERNAME/educa-ai-backend`
2. You should see all your files uploaded
3. The README.md will be displayed on the repository homepage

## Common Git Commands for Future Updates

### Making Changes

```bash
# Check status of your files
git status

# Add specific file
git add filename.py

# Add all changed files
git add .

# Commit changes
git commit -m "Description of your changes"

# Push to GitHub
git push origin main
```

### Viewing History

```bash
# View commit history
git log

# View changes
git diff

# View remote repositories
git remote -v
```

### Branching

```bash
# Create new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main

# List all branches
git branch

# Merge branch into main
git checkout main
git merge feature/new-feature

# Push branch to GitHub
git push origin feature/new-feature
```

### Pulling Updates

```bash
# Pull latest changes from GitHub
git pull origin main
```

## Complete Workflow Example

```bash
# 1. Make changes to your files
nano app.py

# 2. Check what changed
git status

# 3. Add changed files
git add app.py

# 4. Commit with descriptive message
git commit -m "Add new endpoint for quiz generation"

# 5. Push to GitHub
git push origin main
```

## Quick Setup Script

Copy and run this entire script (replace YOUR_USERNAME):

```bash
#!/bin/bash

# Initialize repository
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: World-Class Medical Learning AI Backend"

# Add remote (REPLACE YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/educa-ai-backend.git

# Push to GitHub
git branch -M main
git push -u origin main

echo "✅ Repository pushed to GitHub successfully!"
```

## Important Notes

### Files Excluded by .gitignore

The following files/folders will NOT be uploaded to GitHub:

- `__pycache__/` - Python cache files
- `.env` - Environment variables (contains API keys - KEEP THIS SECRET!)
- `*.pkl` and `*.faiss` - Knowledge base files (optional, can be regenerated)
- Virtual environment folders (`venv/`, `env/`)
- Log files and temporary files

### Security Best Practices

⚠️ **NEVER commit your `.env` file with API keys!**

If you accidentally commit sensitive data:

```bash
# Remove file from git history
git rm --cached .env

# Commit the removal
git commit -m "Remove .env file"

# Update .gitignore to prevent future commits
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Update .gitignore"

# Push changes
git push origin main

# IMPORTANT: Regenerate any exposed API keys immediately!
```

## Recommended Repository Description

```
🎓 World-Class Medical Learning AI Backend

A comprehensive NEET preparation platform featuring:
- 🤖 Multi-Agent Specialist System (Anatomy, Physiology, Biochemistry, Pathology, Pharmacology)
- 🧠 RAG-Enhanced Knowledge Base with 1,558+ lines of medical content
- 📚 8 Advanced Teaching Modes (Socratic, Clinical Cases, Mnemonics, Quiz, etc.)
- 🎯 NEET-Focused Exam Preparation
- 🔍 Intelligent Question Routing
- 📝 Personalized Study Plans & Adaptive Learning

Built with Flask, Google Gemini AI, and FAISS vector search.
```

## Tags to Add on GitHub

```
medical-education
neet-preparation
ai-tutor
flask-api
rag-system
multi-agent-system
machine-learning
educational-technology
gemini-ai
medical-ai
```

## Creating a Good README Badge Section

Add these at the top of your README.md:

```markdown
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
```

---

## Troubleshooting

### Issue: "fatal: remote origin already exists"

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/educa-ai-backend.git
```

### Issue: "Updates were rejected"

```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

### Issue: Authentication failed

```bash
# Use Personal Access Token instead of password
# Generate token at: https://github.com/settings/tokens
# Use token as password when prompted
```

---

**Quick Start:**

```bash
cd /Users/danussh/Desktop/educa-ai-backend
git init
git add .
git commit -m "Initial commit: World-Class Medical Learning AI Backend"
git remote add origin https://github.com/YOUR_USERNAME/educa-ai-backend.git
git branch -M main
git push -u origin main
```

🎉 Your code is now on GitHub!
