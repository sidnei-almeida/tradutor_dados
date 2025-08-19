@echo off
chcp 65001 >nul
echo ========================================
echo    Tradutor de Dados Universal - Windows
echo ========================================
echo.

echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Instale Python 3.10+ em: https://python.org
    pause
    exit /b 1
)
echo ✅ Python encontrado!

echo.
echo [2/5] Criando ambiente virtual...
if exist "venv" (
    echo ⚠️  Ambiente virtual já existe. Removendo...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo ❌ Erro ao criar ambiente virtual!
    pause
    exit /b 1
)
echo ✅ Ambiente virtual criado!

echo.
echo [3/5] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erro ao ativar ambiente virtual!
    pause
    exit /b 1
)
echo ✅ Ambiente virtual ativado!

echo.
echo [4/5] Instalando dependências...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Erro ao instalar dependências!
    pause
    exit /b 1
)
echo ✅ Dependências instaladas!

echo.
echo [5/5] Instalando dependências extras para Windows...
pip install pyinstaller
echo ✅ Dependências extras instaladas!

echo.
echo ========================================
echo 🎉 Instalação concluída com sucesso!
echo ========================================
echo.
echo Para executar a aplicação:
echo   - Duplo-clique em: run.bat
echo   - Ou execute: python app_customtkinter_ux.py
echo.
echo Para gerar o executável:
echo   - Execute: build.bat
echo.
pause
