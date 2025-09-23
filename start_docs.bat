@echo off
echo Installing and Starting Drought Proofing Tool Documentation...
echo.
echo Installing MkDocs and Material theme...
pip install mkdocs mkdocs-material
echo.
echo Starting documentation server...
echo The documentation will open at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0"
mkdocs serve
pause