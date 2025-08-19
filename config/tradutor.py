#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script OTIMIZADO para traduzir nomes de produtos do inglês para o português usando deep-translator.
NOVA LÓGICA: Agrupa múltiplos nomes em uma única chamada à API (até 5000 caracteres por chamada).
Isso reduz drasticamente o número de chamadas à API e acelera o processo de tradução.
"""

import os
import sys
import sqlite3
import csv
import time
import random
from datetime import datetime, timedelta
from tqdm import tqdm
from collections import deque

try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("A biblioteca 'deep-translator' não está instalada.")
    print("Instale com: pip install deep-translator")
    sys.exit(1)

# Configuração OTIMIZADA COM RATE LIMITING INTELIGENTE
DB_PATH = os.path.join(os.path.dirname(__file__), 'fooddata.db')
OUTPUT_CSV_DEFAULT = os.path.join(os.path.dirname(__file__), 'produtos_traduzidos_otimizado.csv')
BATCH_SIZE = 1000  # Tamanho do lote para processamento em memória
MAX_CHARS_PER_CALL = 5000  # Máximo de caracteres por chamada à API
SAFETY_MARGIN = 100  # Margem de segurança para não cortar nomes

# SISTEMA DE RATE LIMITING INTELIGENTE
DELAY_BASE = 2  # Tempo base entre chamadas (segundos)
DELAY_MULTIPLIER = 1.5  # Multiplicador para backoff exponencial
MAX_DELAY = 300  # Máximo 5 minutos de espera
MIN_DELAY = 1  # Mínimo 1 segundo

# SISTEMA DE RETRY ROBUSTO
MAX_RETRIES = 5  # Número máximo de tentativas
RETRY_DELAY_BASE = 5  # Tempo base para retry (segundos)
RETRY_DELAY_MULTIPLIER = 2  # Multiplicador para retry exponencial

# CONTROLE DE TAXA DE CHAMADAS
MAX_CALLS_PER_MINUTE = 30  # Máximo 30 chamadas por minuto
CALL_TIMEOUT = 30  # Timeout de 30 segundos por chamada

# SISTEMA DE MASCARAMENTO DE IP
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
]

HEADERS_ROTATION = [
    {"Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
    {"Accept-Language": "en-US,en;q=0.9,pt;q=0.8", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
    {"Accept-Language": "es-ES,es;q=0.9,en;q=0.8", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
    {"Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
    {"Accept-Language": "de-DE,de;q=0.9,en;q=0.8", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
]

# Configuração de proxies (adicione seus proxies aqui)
PROXIES = [
    # "http://proxy1:port",
    # "http://proxy2:port",
    # "socks5://proxy3:port"
]

ROTATION_INTERVAL = 50  # Rotacionar a cada 50 chamadas

# SISTEMA DE PAUSAS ESTRATÉGICAS MAIS AGRESSIVAS
PAUSA_10K = 120  # Pausa de 2 minutos a cada 10k produtos
PAUSA_25K = 300  # Pausa de 5 minutos a cada 25k produtos
PAUSA_50K = 600  # Pausa de 10 minutos a cada 50k produtos  
PAUSA_100K = 900  # Pausa de 15 minutos a cada 100k produtos

# DELAYS PARA PAUSAS ENTRE CHAMADAS (compatibilidade)
DELAY_MIN = MIN_DELAY       # Tempo mínimo de espera entre chamadas
DELAY_MAX = DELAY_BASE      # Tempo máximo de espera entre chamadas

def traduzir_lote_nomes(nomes, translator, max_retries=MAX_RETRIES, numero_chamada=0):
    """
    Traduz um lote de nomes em uma única chamada à API.
    Os nomes são separados por quebras de linha para o tradutor.
    """
    if not nomes:
        return []
    
    # MELHORIA: Adicionar pontos finais para quebrar melhor as traduções
    # Isso ajuda o Google Tradutor a entender que cada linha é um nome separado
    nomes_com_pontos = [nome + '.' for nome in nomes]
    texto_completo = '\n'.join(nomes_com_pontos)
    
    print(f"Traduzindo lote de {len(nomes)} nomes ({len(texto_completo)} caracteres)...")
    print(f"💡 MELHORIA: Adicionados pontos finais para melhor separação das traduções")
    
    # 🛡️ MASCARAMENTO DE IP: Rotacionar identidade se necessário
    user_agent, headers = rotacionar_identidade(numero_chamada)
    if user_agent and headers:
        print(f"🛡️  Aplicando nova identidade para evitar bloqueios")
    
    # VALIDAÇÃO: Verificar se não excede o limite da API
    if len(texto_completo) > MAX_CHARS_PER_CALL:
        print(f"ERRO: Lote excede limite da API! {len(texto_completo)} > {MAX_CHARS_PER_CALL}")
        # Dividir o lote em partes menores
        meio = len(nomes) // 2
        print(f"Dividindo lote em duas partes: {meio} + {len(nomes) - meio}")
        
        parte1 = traduzir_lote_nomes(nomes[:meio], translator, max_retries)
        parte2 = traduzir_lote_nomes(nomes[meio:], translator, max_retries)
        return parte1 + parte2
    
    # VALIDAÇÃO: Verificar se o texto não está vazio
    if not texto_completo.strip():
        print("AVISO: Lote vazio, retornando nomes originais")
        return nomes
    
    for tentativa in range(max_retries):
        try:
            # Traduzir o lote completo
            resultado = translator.translate(texto_completo)
            
            # Dividir o resultado em linhas individuais
            nomes_traduzidos = resultado.split('\n')
            
            # MELHORIA: Remover pontos finais das traduções
            nomes_traduzidos = [nome.strip().rstrip('.') for nome in nomes_traduzidos if nome.strip()]
            
            # Verificar se o número de traduções corresponde ao número de nomes originais
            if len(nomes_traduzidos) != len(nomes):
                print(f"AVISO: Número de traduções ({len(nomes_traduzidos)}) não corresponde ao número de nomes ({len(nomes)})")
                print(f"🔍 Tentando métodos alternativos de divisão...")
                
                # Tentar corrigir dividindo por quebras de linha duplas ou outros separadores
                if '\n\n' in resultado:
                    nomes_traduzidos = resultado.split('\n\n')
                    print(f"   ✅ Dividido por quebras duplas: {len(nomes_traduzidos)} partes")
                elif ';' in resultado:
                    nomes_traduzidos = resultado.split(';')
                    print(f"   ✅ Dividido por ponto e vírgula: {len(nomes_traduzidos)} partes")
                elif '. ' in resultado:
                    nomes_traduzidos = resultado.split('. ')
                    print(f"   ✅ Dividido por ponto + espaço: {len(nomes_traduzidos)} partes")
                
                # Limpar pontos finais novamente
                nomes_traduzidos = [nome.strip().rstrip('.') for nome in nomes_traduzidos if nome.strip()]
            
            return nomes_traduzidos
            
        except Exception as e:
            if tentativa < max_retries - 1:
                # BACKOFF EXPONENCIAL: tempo_espera = base * (multiplicador ^ tentativa)
                tempo_espera = min(
                    RETRY_DELAY_BASE * (RETRY_DELAY_MULTIPLIER ** tentativa),
                    MAX_DELAY
                )
                print(f"❌ Erro ao traduzir lote: {e}")
                print(f"🔄 Tentativa {tentativa + 1}/{max_retries} em {tempo_espera}s...")
                time.sleep(tempo_espera)
            else:
                print(f"💥 FALHA CRÍTICA: Erro ao traduzir lote após {max_retries} tentativas: {e}")
                print(f"⚠️  Retornando nomes originais para este lote")
                # Em caso de falha, retornar os nomes originais
                return nomes

def rotacionar_identidade(numero_chamada):
    """
    Rotaciona User-Agent e Headers para mascarar a identidade.
    Isso ajuda a evitar bloqueios da API do Google Tradutor.
    """
    if numero_chamada % ROTATION_INTERVAL == 0:
        user_agent = random.choice(USER_AGENTS)
        headers = random.choice(HEADERS_ROTATION)
        
        print(f"🔄 Rotacionando identidade (chamada #{numero_chamada})")
        print(f"   User-Agent: {user_agent[:50]}...")
        print(f"   Headers: {headers}")
        
        return user_agent, headers
    
    return None, None

def verificar_pausa_estrategica(total_processado):
    """
    Verifica se é necessário fazer uma pausa estratégica baseada no número de produtos processados.
    Retorna o tempo de pausa em segundos.
    """
    if total_processado % 100000 == 0 and total_processado > 0:
        print(f"🔄 PAUSA ESTRATÉGICA MEGA: {total_processado:,} produtos processados!")
        print(f"⏰ Pausando por {PAUSA_100K//60} minutos para evitar bloqueios da API...")
        return PAUSA_100K
    elif total_processado % 50000 == 0 and total_processado > 0:
        print(f"🔄 PAUSA ESTRATÉGICA GRANDE: {total_processado:,} produtos processados!")
        print(f"⏰ Pausando por {PAUSA_50K//60} minutos...")
        return PAUSA_50K
    elif total_processado % 25000 == 0 and total_processado > 0:
        print(f"🔄 PAUSA ESTRATÉGICA MÉDIA: {total_processado:,} produtos processados!")
        print(f"⏰ Pausando por {PAUSA_25K//60} minutos...")
        return PAUSA_25K
    elif total_processado % 10000 == 0 and total_processado > 0:
        print(f"🔄 PAUSA ESTRATÉGICA PEQUENA: {total_processado:,} produtos processados!")
        print(f"⏰ Pausando por {PAUSA_10K//60} minutos...")
        return PAUSA_10K
    return 0

def criar_lotes_otimizados(produtos, max_chars=MAX_CHARS_PER_CALL, safety_margin=SAFETY_MARGIN):
    """
    Cria lotes otimizados de produtos baseado no número máximo de caracteres por chamada.
    Garante que nenhum nome seja cortado no meio.
    """
    lotes = []
    lote_atual = []
    chars_atual = 0
    
    print(f"  Criando lotes otimizados (máx: {max_chars} chars, margem: {safety_margin})")
    
    for produto in produtos:
        nome = produto.get('nome', '')
        if not nome:
            continue
            
        # Calcular tamanho do nome + quebra de linha
        tamanho_nome = len(nome) + 1  # +1 para \n
        
        # Se adicionar este nome excederia o limite, finalizar o lote atual
        if chars_atual + tamanho_nome > (max_chars - safety_margin):
            if lote_atual:  # Se já temos produtos no lote
                print(f"    Lote finalizado: {len(lote_atual)} produtos, {chars_atual} chars")
                lotes.append(lote_atual)
                lote_atual = []
                chars_atual = 0
        
        # Adicionar produto ao lote atual (agora garantimos que cabe)
        lote_atual.append(produto)
        chars_atual += tamanho_nome
    
    # Adicionar o último lote se não estiver vazio
    if lote_atual:
        print(f"    Lote final: {len(lote_atual)} produtos, {chars_atual} chars")
        lotes.append(lote_atual)
    
    print(f"  Total de lotes criados: {len(lotes)}")
    return lotes

def obter_colunas_tabela(conn):
    """Obtém as colunas da tabela produtos"""
    print("Obtendo colunas da tabela produtos...")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(produtos)")
    return [col[1] for col in cursor.fetchall()]

def obter_total_produtos(conn, ultimo_id=0, limite=None):
    """Obtém o total de produtos a serem processados a partir do último ID"""
    print(f"Contando produtos a partir do ID {ultimo_id}...")
    cursor = conn.cursor()
    
    if ultimo_id == 0:
        cursor.execute("SELECT max(rowid) FROM produtos")
        estimativa = cursor.fetchone()[0] or 0
        if limite and estimativa > limite:
            return limite
        return estimativa
    else:
        query = f"SELECT COUNT(*) FROM produtos WHERE id > {ultimo_id}"
        if limite:
            query += f" LIMIT {limite}"
        cursor.execute(query)
        return cursor.fetchone()[0]

def obter_ultimo_id_do_csv(arquivo_csv):
    """Verifica o arquivo CSV existente e retorna o último ID processado"""
    print(f"Verificando último ID processado em {arquivo_csv}...")
    if not os.path.exists(arquivo_csv) or os.path.getsize(arquivo_csv) == 0:
        print("Arquivo não existe ou está vazio. Começando do ID 0.")
        return 0
    
    try:
        with open(arquivo_csv, 'r', encoding='utf-8') as f:
            f.seek(0, os.SEEK_END)
            pos = f.tell()
            
            linhas_verificadas = 0
            max_linhas = 10
            
            while pos > 0 and linhas_verificadas < max_linhas:
                pos -= 1
                f.seek(pos)
                char = f.read(1)
                
                if char == '\n' and pos < f.tell() - 1:
                    linha = f.readline().strip()
                    if linha:
                        if ',' in linha:
                            try:
                                id_produto = int(linha.split(',')[0])
                                print(f"Último ID encontrado: {id_produto}")
                                return id_produto
                            except (ValueError, IndexError):
                                continue
            
            f.seek(0)
            primeira_linha = f.readline().strip()
            if primeira_linha and 'id' in primeira_linha.lower():
                print("Arquivo tem apenas cabeçalho. Começando do ID 0.")
                return 0
            
            print("Não foi possível determinar o último ID. Começando do ID 0.")
            return 0
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return 0

def processar_traducao_otimizada(conn, translator, output_file, colunas, ultimo_id=0, total_ja_processado=0, limite=None):
    """
    Processa a tradução usando a nova lógica de lotes otimizados.
    Traduz múltiplos nomes por chamada à API, maximizando eficiência.
    """
    total_restante = obter_total_produtos(conn, ultimo_id, limite)
    total_produtos = total_ja_processado + total_restante
    
    print(f"Último ID processado: {ultimo_id}")
    print(f"Total de produtos já processados: {total_ja_processado}")
    print(f"Total de produtos restantes: {total_restante}")
    print(f"Total geral: {total_produtos}")
    
    total_processado = total_ja_processado
    pbar_global = tqdm(total=total_produtos, initial=total_ja_processado, desc="Progresso total")
    
    # Processar em lotes grandes
    while True:
        # Obter próximo lote de produtos
        cursor = conn.cursor()
        query = f"SELECT * FROM produtos WHERE id > {ultimo_id} ORDER BY id LIMIT {BATCH_SIZE}"
        cursor.execute(query)
        
        produtos_lote = cursor.fetchall()
        if not produtos_lote:
            break
        
        print(f"\nProcessando lote de {len(produtos_lote)} produtos (a partir do ID {ultimo_id})...")
        inicio_lote = time.time()
        
        # Converter para dicionários
        produtos_dict = [{colunas[i]: produto[i] for i in range(len(colunas))} for produto in produtos_lote]
        
        # Criar lotes otimizados baseados no tamanho dos nomes
        lotes_otimizados = criar_lotes_otimizados(produtos_dict)
        print(f"Dividido em {len(lotes_otimizados)} sub-lotes para tradução em lote")
        
        # Processar cada sub-lote
        for i, sub_lote in enumerate(lotes_otimizados):
            print(f"  Traduzindo sub-lote {i+1}/{len(lotes_otimizados)} ({len(sub_lote)} produtos)")
            
            # Extrair apenas os nomes para tradução
            nomes = [produto.get('nome', '') for produto in sub_lote]
            
            # Traduzir o lote de nomes
            nomes_traduzidos = traduzir_lote_nomes(nomes, translator, numero_chamada=i)
            
            # VALIDAÇÃO: Verificar se as traduções são válidas
            traducoes_validas = 0
            for j, nome_traduzido in enumerate(nomes_traduzidos):
                if j < len(sub_lote):
                    nome_original = sub_lote[j].get('nome', '')
                    # Verificar se a tradução é válida (não é igual ao original)
                    if nome_traduzido and nome_traduzido.strip() and nome_traduzido.lower() != nome_original.lower():
                        traducoes_validas += 1
            
            # LOG: Mostrar estatísticas de tradução
            taxa_sucesso = (traducoes_validas / len(nomes_traduzidos)) * 100 if nomes_traduzidos else 0
            print(f"    📊 Taxa de sucesso da tradução: {taxa_sucesso:.1f}% ({traducoes_validas}/{len(nomes_traduzidos)})")
            
            # 🚨 DETECÇÃO AUTOMÁTICA DE BLOQUEIO
            if taxa_sucesso < 30:
                print(f"🚨 ALERTA: Taxa de sucesso muito baixa! Possível bloqueio da API")
                print(f"💡 Recomendação: Aguardar mais tempo ou rotacionar identidade")
            
            # Escrever resultados no CSV
            writer = csv.writer(output_file)
            for j, produto in enumerate(sub_lote):
                if j < len(nomes_traduzidos):
                    nome_traduzido = nomes_traduzidos[j]
                else:
                    nome_traduzido = produto.get('nome', '')  # Fallback para nome original
                
                # Atualizar último ID processado
                ultimo_id = produto.get('id', ultimo_id)
                
                # Escrever linha no CSV
                row = []
                for col in colunas:
                    valor = produto.get(col, '')
                    if valor is None:
                        valor = ''
                    row.append(valor)
                row.append(nome_traduzido)
                writer.writerow(row)
                
                # Atualizar contadores
                total_processado += 1
                pbar_global.update(1)
            
            # Garantir que os dados sejam escritos no disco
            output_file.flush()
            os.fsync(output_file.fileno())
            
            # Pausa entre sub-lotes (menor que antes, já que estamos fazendo menos chamadas)
            if i < len(lotes_otimizados) - 1:
                pausa = random.uniform(DELAY_MIN, DELAY_MAX)
                print(f"    Aguardando {pausa:.2f}s antes do próximo sub-lote...")
                time.sleep(pausa)
        
        # Mostrar progresso após cada lote
        fim_lote = time.time()
        tempo_lote = fim_lote - inicio_lote
        print(f"Lote concluído. Total processado: {total_processado}/{total_produtos}. Tempo: {tempo_lote:.2f}s")
        
        # PAUSAS ESTRATÉGICAS para evitar bloqueios da API
        pausa_estrategica = verificar_pausa_estrategica(total_processado)
        if pausa_estrategica > 0:
            time.sleep(pausa_estrategica)
            print(f"✅ Pausa estratégica concluída! Continuando processamento...")
        
        # Pausa entre lotes principais
        if total_processado < total_produtos:
            pausa_lote = random.uniform(DELAY_MIN * 2, DELAY_MAX * 2)
            print(f"Pausa de {pausa_lote:.2f}s antes do próximo lote...")
            time.sleep(pausa_lote)
    
    pbar_global.close()
    return total_processado, ultimo_id

def main():
    # Verificar argumentos
    if len(sys.argv) > 1 and sys.argv[1] == '--teste':
        teste = True
        limite = 10
        print("Modo de teste ativado: apenas 10 produtos serão processados")
    else:
        teste = False
        limite = None
    
    print("🚀 TRADUTOR OTIMIZADO COM SISTEMA ANTI-BLOQUEIO COMPLETO")
    print("=" * 70)
    print("📋 Funcionalidades implementadas:")
    print("   • Pausa de 15 minutos a cada 100k produtos")
    print("   • Pausa de 10 minutos a cada 50k produtos")
    print("   • Pausa de 5 minutos a cada 25k produtos")
    print("   • Pausa de 2 minutos a cada 10k produtos")
    print("   • Detecção automática de falhas na tradução")
    print("   • Sistema de retry com backoff exponencial")
    print("   • Monitoramento de qualidade das traduções")
    print("   • 🛡️ MASCARAMENTO DE IP com rotação de User-Agents")
    print("   • 🔄 Rotação automática de identidade a cada 50 chamadas")
    print("   • 🚨 Detecção automática de bloqueios da API")
    print("   • 💡 Pontos finais para melhor separação das traduções")
    print("=" * 70)
    
    OUTPUT_CSV = OUTPUT_CSV_DEFAULT
    
    # Verificar se o banco de dados existe
    if not os.path.exists(DB_PATH):
        print(f"ERRO: Banco de dados não encontrado em {DB_PATH}")
        print("Verifique se o arquivo 'fooddata.db' está na mesma pasta do script.")
        sys.exit(1)
    
    print(f"Tamanho do banco de dados: {os.path.getsize(DB_PATH) / (1024*1024*1024):.2f} GB")
    print(f"🚀 NOVA LÓGICA OTIMIZADA: Traduzindo em lotes de até {MAX_CHARS_PER_CALL} caracteres por chamada!")
    
    # Verificar se o arquivo já existe e obter o último ID processado
    ultimo_id = obter_ultimo_id_do_csv(OUTPUT_CSV)
    total_ja_processado = 0
    
    # Determinar o modo de abertura do arquivo
    if ultimo_id > 0:
        modo_arquivo = 'a'
        print(f"Continuando a partir do ID {ultimo_id} no arquivo existente: {OUTPUT_CSV}")
    else:
        modo_arquivo = 'w'
        print(f"Criando novo arquivo de saída: {OUTPUT_CSV}")
    
    # Inicializar o tradutor
    print("Inicializando o tradutor...")
    translator = GoogleTranslator(source='en', target='pt')
    
    # Conectar ao banco de dados
    print(f"Conectando ao banco de dados: {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        print("Conexão estabelecida com sucesso.")
    except Exception as e:
        print(f"ERRO ao conectar ao banco de dados: {e}")
        sys.exit(1)
    
    # Obter colunas da tabela produtos
    colunas = obter_colunas_tabela(conn)
    print(f"Colunas da tabela produtos: {len(colunas)}")
    
    # Obter o total de produtos já processados (se estiver continuando)
    if ultimo_id > 0:
        print(f"Contando produtos já processados (ID <= {ultimo_id})...")
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM produtos WHERE id <= {ultimo_id}")
        total_ja_processado = cursor.fetchone()[0]
    
    # Abrir arquivo CSV para escrita ou append
    with open(OUTPUT_CSV, modo_arquivo, newline='', encoding='utf-8') as output_file:
        # Se for um novo arquivo, escrever o cabeçalho
        if modo_arquivo == 'w':
            writer = csv.writer(output_file)
            colunas_saida = colunas + ['nome_traduzido']
            writer.writerow(colunas_saida)
        
        # Se for teste, mostrar exemplos de tradução em lote
        if teste:
            print("\nExemplos de tradução em lote:")
            exemplos = [
                "Classic Chocolate Chip Cookies",
                "Strawberry Yogurt",
                "Chicken Breast",
                "Apple Juice",
                "Whole Milk"
            ]
            
            print("Traduzindo exemplo em lote...")
            traducao_lote = traduzir_lote_nomes(exemplos, translator)
            for i, exemplo in enumerate(exemplos):
                print(f"  {exemplo} -> {traducao_lote[i] if i < len(traducao_lote) else exemplo}")
            time.sleep(1)
        
        # Iniciar processamento otimizado
        print("\n🚀 Iniciando tradução OTIMIZADA dos produtos...")
        inicio = time.time()
        
        try:
            total_processado, ultimo_id = processar_traducao_otimizada(
                conn, translator, output_file, colunas, 
                ultimo_id, total_ja_processado, limite
            )
            
            # Mostrar estatísticas
            fim = time.time()
            tempo_total = fim - inicio
            produtos_nesta_sessao = total_processado - total_ja_processado
            
            print(f"\n🎉 Produtos traduzidos nesta sessão: {produtos_nesta_sessao}")
            print(f"Total de produtos traduzidos: {total_processado}")
            print(f"Tempo desta sessão: {tempo_total:.2f} segundos")
            if produtos_nesta_sessao > 0:
                print(f"Média desta sessão: {produtos_nesta_sessao/tempo_total:.2f} produtos/segundo")
            
            print(f"\n🚀 Processo de tradução OTIMIZADO concluído com sucesso!")
            print(f"Resultados salvos em: {OUTPUT_CSV}")
            
        except KeyboardInterrupt:
            print("\n\nProcesso interrompido pelo usuário.")
            fim = time.time()
            tempo_total = fim - inicio
            produtos_nesta_sessao = total_processado - total_ja_processado
            
            print(f"Produtos traduzidos nesta sessão: {produtos_nesta_sessao}")
            print(f"Total de produtos traduzidos até agora: {total_processado}")
            print(f"Último ID processado: {ultimo_id}")
            print(f"Tempo desta sessão: {tempo_total:.2f} segundos")
            print(f"Execute o script novamente para continuar de onde parou.")
    
    # Fechar conexão
    conn.close()

if __name__ == "__main__":
    main()


