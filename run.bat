@echo off
chcp 65001 >nul
echo ========================================
echo    Tradutor de Dados Universal - Windows
echo ========================================
echo.

echo [1/3] Verificando ambiente virtual...
if not exist "venv" (
    echo ❌ Ambiente virtual não encontrado!
    echo Execute primeiro: install.bat
    pause
    exit /b 1
)

echo.
echo [2/3] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erro ao ativar ambiente virtual!
    pause
    exit /b 1
)

echo.
echo [3/3] Iniciando aplicação...
echo 🚀 A aplicação será aberta em uma janela desktop
echo.
echo Para parar a aplicação, feche a janela ou pressione Ctrl+C
echo.
python app_customtkinter_ux.py

echo.
echo Aplicação encerrada.
pause
