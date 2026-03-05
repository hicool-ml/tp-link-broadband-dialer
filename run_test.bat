@echo off
chcp 65001 > nul
echo ========================================
echo TP-Link Broadband Dialer Service
echo Test Script
echo ========================================
echo.

echo Running service tests...
echo.

python test_service.py

if errorlevel 1 (
    echo.
    echo Some tests failed. Please check the output above.
    echo.
) else (
    echo.
    echo All tests passed!
    echo.
)

pause
