# Publish StreamSphere PoC to GitHub

Local git repo is already initialized with the first commit on branch `master`.
`.env` is ignored so secrets are not committed.

## Option A — GitHub website (simplest)

1. Go to https://github.com/new
2. Repository name suggestion: `StreamSphere-PoC` or `AODB-Group3-StreamSphere-PoC`
3. Set visibility to **Public** (or Private + invite instructor)
4. Do **not** add README / .gitignore / license (repo already has files)
5. Create repository
6. In PowerShell:

```powershell
$env:Path = "C:\Program Files\Git\cmd;" + $env:Path
cd "D:\MSIT\Subjects\AODB\Group Project\StreamSphere_PoC"

# replace YOURUSER with your GitHub username
git remote add origin https://github.com/YOURUSER/StreamSphere-PoC.git
git branch -M main
git push -u origin main
```

7. Copy the repo URL into your Phase 6 / final report.

## Option B — GitHub CLI

```powershell
winget install --id GitHub.cli --source winget --accept-package-agreements --accept-source-agreements
# reopen terminal, then:
gh auth login
cd "D:\MSIT\Subjects\AODB\Group Project\StreamSphere_PoC"
gh repo create StreamSphere-PoC --public --source=. --remote=origin --push
```

## After publishing

Add these to the report:

- GitHub repository link
- Clone/run instructions from `README.md`
- Note that TMDB key (if used) stays in local `.env`, not in GitHub
