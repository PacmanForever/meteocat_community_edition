@echo off
cd /d c:\Jordi\meteocat_community_edition
git config user.email "release@meteocat.local"
git config user.name "Release Bot"
echo git tag -a v1.0.0 -m "Release v1.0.0 (2025-11-29)" 2>nul
git push origin main
echo git push origin v1.0.0
echo.
echo Release pushed to GitHub. GitHub Actions will run tests automatically.
pause