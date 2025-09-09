@echo off 
title QuaNThoR - Triple-AI Mathematical Verification System 
color 0B 
echo. 
echo ======================================================== 
echo    QuaNThoR - Triple-AI Mathematical Verification 
echo    Starting Web Server... 
echo ======================================================== 
echo. 
echo Server starting at: http://localhost:5000 
echo. 
echo INSTRUCTIONS FOR STUDENTS: 
echo 1. Wait for "Running on http://127.0.0.1:5000" message 
echo 2. Open your web browser 
echo 3. Go to: http://localhost:5000 
echo 4. Start verifying mathematical proofs! 
echo. 
echo Press Ctrl+C to stop the server when done 
echo. 
cd /d "C:\Users\jeans\Desktop\QuaNThoR\" 
python src/app.py 
pause 
