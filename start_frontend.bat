@echo off
echo Starting Face Recognition Frontend...
echo.
cd frontend
echo Installing dependencies...
npm install
echo.
echo Starting development server on http://localhost:3001
echo Press Ctrl+C to stop the server
echo.
npm run dev
pause
