@echo off
echo Starting TP-Link Shutdown Cleanup Service...
sc start TPLinkShutdownCleanup
echo.
echo Checking service status...
sc query TPLinkShutdownCleanup
echo.
pause
