@echo off
REM Script para executar OFX Consolidador Pro no Windows

echo ================================================
echo   OFX Consolidador Pro v3.0
echo   Por: Tiago Schubert
echo ================================================
echo.

REM Ativa ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    echo Ativando ambiente virtual...
    call venv\Scripts\activate.bat
)

REM Executa a aplicação GUI
echo Iniciando aplicação...
python main_gui.py

pause
