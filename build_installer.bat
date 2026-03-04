@echo off  
cd /d "%%~dp0"  
  
echo Building installer...  
if not exist "Release" mkdir "Release"  
"C:\Program Files (x86)\NSIS\makensis.exe" "installer.nsi"  
