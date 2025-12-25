@echo off
REM Script de instalação para OFX Consolidador Pro no Windows

echo ================================================
echo   OFX Consolidador Pro - Instalação
echo   Por: Tiago Schubert
echo ================================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não encontrado!
    echo Por favor, instale o Python 3.8 ou superior de https://www.python.org/
    pause
    exit /b 1
)

echo Python encontrado!
python --version
echo.

REM Cria ambiente virtual se não existir
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
    echo Ambiente virtual criado!
    echo.
)

REM Ativa ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Atualiza pip
echo Atualizando pip...
python -m pip install --upgrade pip
echo.

REM Instala dependências
echo Instalando dependências...
pip install -r requirements.txt
echo.

if errorlevel 1 (
    echo.
    echo ERRO: Falha na instalação de dependências!
    echo Por favor, verifique o arquivo de log acima.
    pause
    exit /b 1
)

echo ================================================
echo   Instalação concluída com sucesso!
echo ================================================
echo.
echo Para executar a aplicação, use: RUN_GUI.bat
echo.
pause
