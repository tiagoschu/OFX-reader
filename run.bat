@echo off
REM Script para executar a aplicação OFX Consolidador no Windows

REM Ativa o ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Executa a aplicação
python app.py

pause
