# Tradutor de Dados Universal

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Interface](https://img.shields.io/badge/GUI-CustomTkinter-1f6feb)](https://github.com/TomSchimansky/CustomTkinter)
[![Plataformas](https://img.shields.io/badge/Plataformas-Linux%20%7C%20macOS-lightgrey)](https://en.wikipedia.org/wiki/Cross-platform)
[![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-green)](./LICENSE)

Aplicação desktop para traduzir datasets (CSV, Excel, SQLite) de forma simples e eficiente. Construída em Python com CustomTkinter, oferece um fluxo direto: carregue o dataset, selecione colunas e traduza com um clique.

---

## ✨ Funcionalidades

- **Interface simples**: layout organizado em 3 colunas (Configurações • Área Central • Logs)
- **Suporte multi-formato**: CSV, Excel e bancos SQLite (com seleção de tabela)
- **Tradução eficiente**: processamento em lotes com controle de delay e uso de memória
- **Tema escuro**: interface com cores escuras para melhor visualização
- **Logs integrados**: histórico de atividades dentro da aplicação
- **Execução simplificada**: script `run.sh` configura o ambiente automaticamente

---

## 🖥️ Captura de Tela

Adicione uma captura da interface em `docs/screenshot-dark.png` para aparecer aqui:

```text
![Interface da Aplicação](docs/screenshot-dark.png)
```

---

## 🚀 Instalação e Execução

### Windows
```batch
# Instalar dependências e criar ambiente
install.bat

# Executar aplicação
run.bat

# Gerar executável standalone
build.bat
```

### Linux/macOS
```bash
chmod +x run.sh
./run.sh
```

### Manual (alternativa)
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate.bat  # Windows
pip install -r requirements.txt
python app_customtkinter_ux.py
```

> Observação: Em distribuições Linux, o `run.sh` tenta instalar dependências de sistema para renderização (Pillow/Tk). Caso seu gerenciador de pacotes não seja suportado, instale manualmente os pacotes equivalentes.

---

## 🎯 Como Usar

1. Selecione o tipo de arquivo: `CSV`, `Excel` ou `SQLite` (para SQLite, escolha a tabela).
2. Escolha idiomas de origem e destino.
3. Carregue o arquivo e marque as colunas que deseja traduzir.
4. Clique em **Iniciar Tradução**. Use **Parar Tradução** para interromper com segurança.
5. Acompanhe progresso e mensagens no card de **Log de Atividades**.

---

## 🎨 Interface

A aplicação usa um tema escuro com:
- Fundo preto e cinzas escuros
- Texto em branco e cinza claro
- Botões em verde para ações principais
- Botões em vermelho para parar/erros
- Layout compacto para aproveitar melhor o espaço da tela

---

## ⚙️ Configurações

- **Tamanho do Lote**: controla quantas linhas são processadas por iteração
- **Delay entre requisições**: evita bloqueios de provedores externos
- **Seleção de Tabela (SQLite)**: combo exibido dinamicamente apenas quando aplicável

Arquivos de configuração:
- `config/settings.json` — parâmetros gerais
- `config/tradutor.py` — lógica de tradução e integração

---

## 🔧 Estrutura do Projeto

```
tradutor_dados/
├── app_customtkinter_ux.py      # Interface principal da aplicação
├── config/
│   ├── settings.json            # Configurações da aplicação
│   └── tradutor.py              # Lógica de tradução/processamento
├── requirements.txt             # Dependências Python
├── run.sh                       # Script de execução para Linux/macOS
├── run.bat                      # Script de execução para Windows
├── install.bat                  # Script de instalação para Windows
├── build.bat                    # Script para gerar executável
├── manage_venv.sh               # Gerenciamento de ambiente virtual
├── dados_teste.csv              # Arquivo de exemplo para testes
├── exemplo_uso.py               # Exemplo de uso da aplicação
├── tradutor.spec                # Configuração para PyInstaller
└── README.md                    # Documentação do projeto
```

---

## 🧪 Roadmap

- [ ] Modo CLI para automação em pipelines
- [ ] Exportações adicionais (Parquet/Feather/SQLite)
- [ ] Perfil de desempenho e cache de traduções
- [ ] Preferências persistentes por projeto
- [ ] Pacote distribuível (AppImage/DMG)

---

## 🐛 Solução de Problemas

- `ModuleNotFoundError: customtkinter`: execute via `./run.sh` ou `pip install -r requirements.txt`
- Problemas de renderização no Linux: instale pacotes do Pillow/Tk da sua distro
- Janela não abre (ambientes remotos): verifique DISPLAY/Wayland/X11

---

## 🤝 Contribuição

1. Faça um fork do repositório
2. Crie sua branch: `git checkout -b feature/nome-da-feature`
3. Commit: `git commit -m "feat: minha melhoria"`
4. Push: `git push origin feature/nome-da-feature`
5. Abra um Pull Request

---

## 📝 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para detalhes.

---

## 🙏 Créditos

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [deep-translator](https://github.com/nidhaloff/deep-translator)
- [pandas](https://pandas.pydata.org/)
- [SQLite](https://www.sqlite.org/)
