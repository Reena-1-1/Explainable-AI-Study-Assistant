# Git steps for everyone (one-time setup, then daily workflow)

## One-time setup
1. Install Python 3.10+ and Git. Create a GitHub account.
2. Accept Reena's collaborator invite (check your email, or github.com/notifications).
3. Open a terminal and run:
```
git config --global user.name "Your Name"
git config --global user.email "your-github-email"
git clone https://github.com/Reena-1-1/Explainable-AI-Study-Assistant.git
cd Explainable-AI-Study-Assistant
python -m venv venv
venv\Scripts\activate            (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
git checkout -b feature/YOUR-BRANCH
```
(first install takes a few minutes: it downloads sentence-transformers)

## Every time you do work
```
git add .
git commit -m "short description of what you did"
git push origin feature/YOUR-BRANCH
```
First push may ask you to log in to GitHub in a browser. Do it.

## Submit your work
On GitHub open the repo -> click "Compare & pull request" -> write a title -> "Create pull request".
Message Reena. She reviews and merges.

## Update your branch with latest main
```
git checkout main
git pull origin main
git checkout feature/YOUR-BRANCH
git merge main
```

## If something goes wrong
Do not delete the folder. Send Reena a screenshot of the error.
