@echo off
cd /d "%~dp0"
echo Iniciando HSF Olho de Deus...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment nao encontrado. Tentando rodar com python global...
)
python gui_app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocorreu um erro na execucao.
    pause
) else (
    echo Aplicacao encerrada normalmente.
    pause
)
