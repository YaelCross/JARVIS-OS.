@echo off
REM Desactiva el inicio automatico de YAELCORE-OS.

set "DESTINO=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\YAELCORE-OS.lnk"

if exist "%DESTINO%" (
    del "%DESTINO%"
    echo [OK] YAELCORE-OS ya no se iniciara al encender la computadora.
) else (
    echo YAELCORE-OS no estaba configurado para iniciar automaticamente.
)

pause
