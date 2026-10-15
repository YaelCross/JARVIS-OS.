@echo off
REM Hace que YAELCORE-OS se inicie automaticamente al encender la computadora
REM (al iniciar sesion en Windows). Crea un acceso directo en la carpeta Inicio.

cd /d "%~dp0"

set "DESTINO=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\YAELCORE-OS.lnk"
set "LANZADOR=%~dp0iniciar_yaelcore.vbs"

if not exist "%~dp0.venv\Scripts\pythonw.exe" (
    echo [!] No se encontro "%~dp0.venv\Scripts\pythonw.exe"
    echo     Crea el entorno virtual e instala las dependencias primero.
    pause
    exit /b 1
)

set "CARPETA=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s = (New-Object -ComObject WScript.Shell).CreateShortcut($env:DESTINO); $s.TargetPath = $env:WINDIR + '\System32\wscript.exe'; $s.Arguments = [char]34 + $env:LANZADOR + [char]34; $s.WorkingDirectory = $env:CARPETA; $s.Description = 'YAELCORE-OS'; $s.Save()"

if exist "%DESTINO%" (
    echo [OK] YAELCORE-OS se iniciara automaticamente al encender la computadora.
    echo      Acceso directo creado en:
    echo      %DESTINO%
) else (
    echo [!] No se pudo crear el acceso directo.
)

pause
