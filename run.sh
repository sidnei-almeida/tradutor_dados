#!/bin/bash

# Script de inicialização para o Tradutor de Dados Universal - Desktop
# Autor: Sistema de Tradução Universal
# Data: $(date)

# Obter o diretório onde está este script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🌐 Tradutor de Dados Universal - Desktop"
echo "========================================="
echo "📁 Diretório do projeto: $(pwd)"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "Por favor, instale Python 3.8 ou superior"
    exit 1
fi

# Verificar versão do Python
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Versão do Python muito antiga: $python_version"
    echo "Requer Python $required_version ou superior"
    exit 1
fi

echo "✅ Python $python_version encontrado"

# Verificar e instalar dependências do sistema para Tkinter
echo ""
echo "🔍 Verificando dependências do sistema para Tkinter..."

# Função para detectar o gerenciador de pacotes
detect_package_manager() {
    if command -v pacman &> /dev/null; then
        echo "pacman"
    elif command -v apt &> /dev/null; then
        echo "apt"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v zypper &> /dev/null; then
        echo "zypper"
    elif command -v brew &> /dev/null; then
        echo "brew"
    else
        echo "unknown"
    fi
}

# Função para instalar dependências do Tkinter
install_tkinter_deps() {
    local pkg_manager=$(detect_package_manager)
    
    case $pkg_manager in
        "pacman")
            echo "📦 Instalando dependências Tkinter via pacman (Arch/CachyOS)..."
            sudo pacman -S --noconfirm tk python-pip
            ;;
        "apt")
            echo "📦 Instalando dependências Tkinter via apt (Debian/Ubuntu)..."
            sudo apt update
            sudo apt install -y python3-tk python3-pip
            ;;
        "dnf"|"yum")
            echo "📦 Instalando dependências Tkinter via dnf/yum (Fedora/RHEL)..."
            sudo dnf install -y tkinter python3-pip || sudo yum install -y tkinter python3-pip
            ;;
        "zypper")
            echo "📦 Instalando dependências Tkinter via zypper (openSUSE)..."
            sudo zypper install -y python3-tk python3-pip
            ;;
        "brew")
            echo "📦 Instalando dependências Tkinter via brew (macOS)..."
            brew install python-tk
            ;;
        *)
            echo "⚠️  Gerenciador de pacotes não reconhecido"
            echo "Por favor, instale manualmente as dependências do Tkinter:"
            echo "  - tk (biblioteca Tk)"
            echo "  - python3-tk (bindings Python para Tk)"
            echo ""
            echo "Para Arch/CachyOS: sudo pacman -S tk python-pip"
            echo "Para Debian/Ubuntu: sudo apt install python3-tk python3-pip"
            echo "Para Fedora/RHEL: sudo dnf install tkinter python3-pip"
            echo "Para openSUSE: sudo zypper install python3-tk python3-pip"
            echo ""
            read -p "Pressione Enter após instalar as dependências manualmente..."
            ;;
    esac
}

# Verificar se Tkinter está disponível
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "❌ Tkinter não encontrado!"
    echo "Instalando dependências do sistema necessárias..."
    
    # Tentar instalar automaticamente
    install_tkinter_deps
    
    # Verificar novamente
    if ! python3 -c "import tkinter" &> /dev/null; then
        echo "❌ Tkinter ainda não está funcionando após instalação automática"
        echo "Por favor, instale manualmente as dependências e tente novamente"
        exit 1
    else
        echo "✅ Tkinter instalado com sucesso!"
    fi
else
    echo "✅ Tkinter já está disponível!"
fi

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo ""
    echo "🔧 Ambiente virtual não encontrado. Criando novo ambiente virtual..."
    
    # Criar ambiente virtual
    if python3 -m venv venv; then
        echo "✅ Ambiente virtual 'venv' criado com sucesso!"
    else
        echo "❌ Erro ao criar ambiente virtual!"
        echo "Verifique se o módulo 'venv' está disponível:"
        echo "  python3 -m venv --help"
        exit 1
    fi
else
    echo "✅ Ambiente virtual 'venv' encontrado!"
fi

PYTHON="$SCRIPT_DIR/venv/bin/python"
PIP="$SCRIPT_DIR/venv/bin/pip"

echo ""
echo "🔄 Usando Python do venv: $PYTHON"
echo "🔄 Usando Pip do venv: $PIP"

# Verificar se pip está disponível no ambiente virtual
if [ ! -x "$PIP" ]; then
    echo "❌ Pip não encontrado no ambiente virtual!"
    echo "Tentando instalar pip..."
    
    # Tentar instalar pip
    if "$PYTHON" -m ensurepip --upgrade; then
        echo "✅ Pip instalado com sucesso!"
    else
        echo "❌ Erro ao instalar pip!"
        echo "Tente executar manualmente: python -m ensurepip --upgrade"
        exit 1
    fi
fi

# Verificar se as dependências estão instaladas
echo ""
echo "🔍 Verificando dependências Python..."

# Lista de dependências principais (incluindo customtkinter)
dependencies=("pandas" "deep_translator" "openpyxl" "xlrd" "customtkinter")

missing_deps=()
for dep in "${dependencies[@]}"; do
    if ! "$PYTHON" -c "import $dep" &> /dev/null; then
        missing_deps+=("$dep")
    fi
done

# Instalar dependências faltantes
if [ ${#missing_deps[@]} -ne 0 ]; then
    echo "📦 Instalando dependências faltantes..."
    echo "Dependências a instalar: ${missing_deps[*]}"
    
    # Atualizar pip primeiro
    echo "🔄 Atualizando pip..."
    "$PIP" install --upgrade pip
    
    # Verificar se customtkinter está na lista de dependências faltantes
    if [[ " ${missing_deps[@]} " =~ " customtkinter " ]]; then
        echo "🎨 CustomTkinter detectado como dependência faltante"
        echo "📦 Instalando dependências do sistema para CustomTkinter..."
        
        # Instalar dependências do sistema para CustomTkinter
        local pkg_manager=$(detect_package_manager)
        case $pkg_manager in
            "pacman")
                echo "📦 Instalando dependências CustomTkinter via pacman (Arch/CachyOS)..."
                sudo pacman -S --noconfirm python-pillow python-pillow-tk
                ;;
            "apt")
                echo "📦 Instalando dependências CustomTkinter via apt (Debian/Ubuntu)..."
                sudo apt update
                sudo apt install -y python3-pil python3-pil.imagetk
                ;;
            "dnf"|"yum")
                echo "📦 Instalando dependências CustomTkinter via dnf/yum (Fedora/RHEL)..."
                sudo dnf install -y python3-pillow python3-pillow-tk || sudo yum install -y python3-pillow python3-pillow-tk
                ;;
            "zypper")
                echo "📦 Instalando dependências CustomTkinter via zypper (openSUSE)..."
                sudo zypper install -y python3-pillow python3-pillow-tk
                ;;
            "brew")
                echo "📦 Instalando dependências CustomTkinter via brew (macOS)..."
                brew install pillow
                ;;
            *)
                echo "⚠️  Gerenciador de pacotes não reconhecido para CustomTkinter"
                echo "Por favor, instale manualmente:"
                echo "  - python3-pillow (PIL/Pillow)"
                echo "  - python3-pillow-tk (suporte Tk para Pillow)"
                ;;
        esac
    fi
    
    # Instalar dependências do requirements.txt
    if [ -f "requirements.txt" ]; then
        echo "📦 Instalando dependências do requirements.txt..."
        if "$PIP" install -r requirements.txt; then
            echo "✅ Dependências instaladas com sucesso!"
        else
            echo "❌ Erro ao instalar dependências do requirements.txt!"
            echo "Tentando instalar dependências individualmente..."
            
            # Instalar dependências individualmente
            for dep in "${missing_deps[@]}"; do
                echo "📦 Instalando $dep..."
                if "$PIP" install "$dep"; then
                    echo "✅ $dep instalado com sucesso!"
                else
                    echo "❌ Erro ao instalar $dep!"
                fi
            done
        fi
    else
        echo "⚠️  Arquivo requirements.txt não encontrado!"
        echo "Instalando dependências individualmente..."
        
        # Instalar dependências individualmente
        for dep in "${missing_deps[@]}"; do
            echo "📦 Instalando $dep..."
            if "$PIP" install "$dep"; then
                echo "✅ $dep instalado com sucesso!"
            else
                echo "❌ Erro ao instalar $dep!"
            fi
        done
    fi
else
    echo "✅ Todas as dependências já estão instaladas!"
fi

# Verificar se a aplicação pode ser executada
echo ""
echo "🔍 Verificando se a aplicação pode ser executada..."

if [ ! -f "app_customtkinter_ux.py" ]; then
    echo "❌ Arquivo app_customtkinter_ux.py não encontrado!"
    echo "Verifique se você está no diretório correto"
    echo "Diretório atual: $(pwd)"
    echo "Arquivos encontrados:"
    ls -la *.py 2>/dev/null || echo "   Nenhum arquivo .py encontrado"
    exit 1
fi

echo "✅ Arquivo app_customtkinter_ux.py encontrado!"

# Verificar se Tkinter funciona no ambiente virtual
echo ""
echo "🔍 Verificando Tkinter no ambiente virtual..."
if ! "$PYTHON" -c "import tkinter; print('Tkinter funcionando!')" &> /dev/null; then
    echo "❌ Tkinter não está funcionando no ambiente virtual!"
    echo "Tentando instalar tkinter no ambiente virtual..."
    
    # Tentar instalar tkinter via pip (pode não funcionar em todos os sistemas)
    if "$PIP" install tk; then
        echo "✅ Tkinter instalado via pip!"
    else
        echo "❌ Não foi possível instalar Tkinter via pip"
        echo "O problema pode ser que o Tkinter precisa ser instalado no sistema"
        echo "Execute o script novamente para tentar instalar as dependências do sistema"
        exit 1
    fi
else
    echo "✅ Tkinter funcionando no ambiente virtual!"
fi

echo ""
echo "🚀 Iniciando Tradutor de Dados Universal - Desktop..."
echo "A aplicação será aberta em uma janela desktop"
echo ""
echo "Para parar a aplicação, feche a janela ou pressione Ctrl+C"
echo ""

# Executar a aplicação usando o Python do venv (substitui o processo atual)
exec "$PYTHON" app_customtkinter_ux.py
echo ""
echo "👋 Ambiente virtual desativado. Até logo!"
