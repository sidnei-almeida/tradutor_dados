@echo off
chcp 65001 >nul
echo ========================================
echo    Gerando Executável - Windows
echo ========================================
echo.

echo [1/4] Verificando ambiente virtual...
if not exist "venv" (
    echo ❌ Ambiente virtual não encontrado!
    echo Execute primeiro: install.bat
    pause
    exit /b 1
)

echo.
echo [2/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Erro ao ativar ambiente virtual!
    pause
    exit /b 1
)

echo.
echo [3/4] Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ❌ PyInstaller não encontrado!
    echo Execute primeiro: install.bat
    pause
    exit /b 1
)

echo.
echo [4/4] Gerando executável...
echo ⏳ Isso pode levar alguns minutos...
echo.
pyinstaller --onefile --windowed --name "Tradutor_Dados_Universal" app_customtkinter_ux.py

if errorlevel 1 (
    echo ❌ Erro ao gerar executável!
    pause
    exit /b 1
)

echo.
echo ========================================
echo 🎉 Executável gerado com sucesso!
echo ========================================
echo.
echo Arquivo criado em: dist\Tradutor_Dados_Universal.exe
echo.
echo Para distribuir:
echo   - Copie o arquivo .exe para qualquer computador Windows
echo   - Não precisa de Python instalado
echo   - Execute com duplo-clique
echo.
pause
