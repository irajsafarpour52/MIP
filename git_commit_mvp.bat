@echo off

echo ==========================
echo MIP Git Commit
echo ==========================

cd /d D:\MIP

echo.
echo Adding files...

git add src/services/meeting_service.py
git add src/writers
git add meeting_report.md
git add .gitignore

echo.
echo Commiting changes...

git commit -m "Add markdown report generation"

echo.
echo Current status:

git status

pause