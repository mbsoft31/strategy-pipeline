@echo off
echo Staging all changes...
git add -A

echo.
echo Committing...
git commit -F commit_msg.txt

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo Done!
pause

