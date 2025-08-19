#!/bin/bash

# Script de gerenciamento do ambiente virtual
# Autor: Sistema de Tradução Universal

VENV_DIR="venv"

show_help() {
    echo "🌐 Gerenciador de Ambiente Virtual - Tradutor de Dados Universal"
    echo "================================================================"
    echo ""
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  create     - Criar novo ambiente virtual"
    echo "  activate   - Ativar ambiente virtual"
    echo "  deactivate - Desativar ambiente virtual"
    echo "  install    - Instalar dependências"
    echo "  update     - Atualizar dependências"
    echo "  clean      - Remover ambiente virtual"
    echo "  status     - Mostrar status do ambiente"
    echo "  help       - Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 create     # Criar novo ambiente virtual"
    echo "  $0 install    # Instalar dependências"
    echo "  $0 status     # Verificar status"
}

create_venv() {
    echo "🔧 Criando novo ambiente virtual..."
    
    if [ -d "$VENV_DIR" ]; then
        echo "⚠️  Ambiente virtual já existe!"
        read -p "Deseja recriar? (s/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            echo "Operação cancelada."
            return
        fi
        clean_venv
    fi
    
    if python3 -m venv "$VENV_DIR"; then
        echo "✅ Ambiente virtual criado com sucesso!"
        echo "📁 Localização: $(pwd)/$VENV_DIR"
        
        # Ativar e instalar dependências
        activate_venv
        install_deps
    else
        echo "❌ Erro ao criar ambiente virtual!"
        echo "Verifique se o módulo 'venv' está disponível:"
        echo "  python3 -m venv --help"
        return 1
    fi
}

activate_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "❌ Ambiente virtual não encontrado!"
        echo "Execute: $0 create"
        return 1
    fi
    
    echo "🔄 Ativando ambiente virtual..."
    source "$VENV_DIR/bin/activate"
    
    if [ $? -eq 0 ]; then
        echo "✅ Ambiente virtual ativado!"
        echo "   Python: $(which python)"
        echo "   Pip: $(which pip)"
        echo "   Versão Python: $(python --version)"
    else
        echo "❌ Erro ao ativar ambiente virtual!"
        return 1
    fi
}

deactivate_venv() {
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
        echo "✅ Ambiente virtual desativado!"
    else
        echo "ℹ️  Nenhum ambiente virtual ativo."
    fi
}

install_deps() {
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "❌ Ambiente virtual não está ativo!"
        echo "Execute: $0 activate"
        return 1
    fi
    
    echo "📦 Instalando dependências..."
    
    # Atualizar pip primeiro
    echo "🔄 Atualizando pip..."
    pip install --upgrade pip
    
    # Instalar dependências do requirements.txt
    if [ -f "requirements.txt" ]; then
        echo "📦 Instalando dependências do requirements.txt..."
        if pip install -r requirements.txt; then
            echo "✅ Dependências instaladas com sucesso!"
        else
            echo "❌ Erro ao instalar dependências do requirements.txt!"
            echo "Tentando instalar dependências principais individualmente..."
            
            # Dependências principais
            deps=("pandas" "deep_translator" "openpyxl" "xlrd")
            for dep in "${deps[@]}"; do
                echo "📦 Instalando $dep..."
                pip install "$dep"
            done
        fi
    else
        echo "⚠️  Arquivo requirements.txt não encontrado!"
        echo "Instalando dependências principais..."
        
        deps=("pandas" "deep_translator" "openpyxl" "xlrd")
        for dep in "${deps[@]}"; do
            echo "📦 Instalando $dep..."
            pip install "$dep"
        done
    fi
}

update_deps() {
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "❌ Ambiente virtual não está ativo!"
        echo "Execute: $0 activate"
        return 1
    fi
    
    echo "🔄 Atualizando dependências..."
    
    # Atualizar pip
    pip install --upgrade pip
    
    # Atualizar dependências
    if [ -f "requirements.txt" ]; then
        pip install --upgrade -r requirements.txt
    else
        # Atualizar dependências principais
        deps=("pandas" "deep_translator" "openpyxl" "xlrd")
        for dep in "${deps[@]}"; do
            echo "🔄 Atualizando $dep..."
            pip install --upgrade "$dep"
        done
    fi
    
    echo "✅ Dependências atualizadas!"
}

clean_venv() {
    if [ -d "$VENV_DIR" ]; then
        echo "🗑️  Removendo ambiente virtual..."
        
        # Desativar se estiver ativo
        if [ -n "$VIRTUAL_ENV" ]; then
            deactivate
        fi
        
        # Remover diretório
        rm -rf "$VENV_DIR"
        echo "✅ Ambiente virtual removido!"
    else
        echo "ℹ️  Nenhum ambiente virtual encontrado."
    fi
}

show_status() {
    echo "📊 Status do Ambiente Virtual"
    echo "============================="
    
    # Verificar se existe
    if [ -d "$VENV_DIR" ]; then
        echo "✅ Ambiente virtual existe: $VENV_DIR"
        
        # Verificar se está ativo
        if [ -n "$VIRTUAL_ENV" ]; then
            echo "🟢 Ambiente virtual ATIVO"
            echo "   Localização: $VIRTUAL_ENV"
            echo "   Python: $(which python)"
            echo "   Versão: $(python --version)"
            echo "   Pip: $(which pip)"
            
            # Verificar dependências
            echo ""
            echo "📦 Dependências instaladas:"
            deps=("pandas" "deep_translator" "openpyxl" "xlrd")
            for dep in "${deps[@]}"; do
                if python -c "import $dep" &> /dev/null; then
                    echo "   ✅ $dep"
                else
                    echo "   ❌ $dep"
                fi
            done
        else
            echo "🔴 Ambiente virtual INATIVO"
            echo "   Execute: $0 activate"
        fi
    else
        echo "❌ Ambiente virtual não encontrado"
        echo "   Execute: $0 create"
    fi
    
    echo ""
            echo "📁 Arquivos da aplicação:"
        if [ -f "app_customtkinter.py" ]; then
            echo "   ✅ app_customtkinter.py (CustomTkinter - RECOMENDADO)"
        else
            echo "   ❌ app_customtkinter.py"
        fi
        
        if [ -f "app_desktop.py" ]; then
            echo "   ✅ app_desktop.py"
        else
            echo "   ❌ app_desktop.py"
        fi
    
    if [ -f "requirements.txt" ]; then
        echo "   ✅ requirements.txt"
    else
        echo "   ❌ requirements.txt"
    fi
}

# Processar comandos
case "${1:-help}" in
    "create")
        create_venv
        ;;
    "activate")
        activate_venv
        ;;
    "deactivate")
        deactivate_venv
        ;;
    "install")
        activate_venv && install_deps
        ;;
    "update")
        activate_venv && update_deps
        ;;
    "clean")
        clean_venv
        ;;
    "status")
        show_status
        ;;
    "help"|*)
        show_help
        ;;
esac
