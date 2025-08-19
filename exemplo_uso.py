#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemplo de uso programático do Tradutor de Dados Universal
Demonstra como usar o sistema de tradução diretamente no código Python
"""

import pandas as pd
from deep_translator import GoogleTranslator
import time

def exemplo_traducao_simples():
    """Exemplo básico de tradução de uma lista de textos"""
    print("🌐 Exemplo de Tradução Simples")
    print("=" * 40)
    
    # Lista de produtos em inglês
    produtos_ingles = [
        "Apple",
        "Banana",
        "Orange Juice",
        "Chicken Breast",
        "Whole Milk",
        "Bread",
        "Cheese",
        "Tomato",
        "Carrot",
        "Potato"
    ]
    
    print(f"Produtos originais: {produtos_ingles}")
    
    # Inicializar tradutor
    translator = GoogleTranslator(source='en', target='pt')
    
    # Traduzir em lote
    print("\n🔄 Traduzindo...")
    produtos_traduzidos = []
    
    for produto in produtos_ingles:
        try:
            traducao = translator.translate(produto)
            produtos_traduzidos.append(traducao)
            print(f"  {produto} → {traducao}")
            time.sleep(0.5)  # Pausa para evitar bloqueio
        except Exception as e:
            print(f"  ❌ Erro ao traduzir '{produto}': {e}")
            produtos_traduzidos.append(produto)  # Manter original em caso de erro
    
    print(f"\n✅ Tradução concluída! {len(produtos_traduzidos)} produtos traduzidos")
    return produtos_traduzidos

def exemplo_traducao_dataframe():
    """Exemplo de tradução de um DataFrame"""
    print("\n📊 Exemplo de Tradução de DataFrame")
    print("=" * 40)
    
    # Criar DataFrame de exemplo
    data = {
        'id': [1, 2, 3, 4, 5],
        'produto_en': ['Apple', 'Banana', 'Orange', 'Grape', 'Strawberry'],
        'categoria_en': ['Fruit', 'Fruit', 'Fruit', 'Fruit', 'Berry'],
        'descricao_en': ['Red apple', 'Yellow banana', 'Orange citrus', 'Purple grape', 'Red berry']
    }
    
    df = pd.DataFrame(data)
    print("DataFrame original:")
    print(df)
    
    # Inicializar tradutor
    translator = GoogleTranslator(source='en', target='pt')
    
    # Traduzir colunas de texto
    colunas_traduzir = ['produto_en', 'categoria_en', 'descricao_en']
    
    print(f"\n🔄 Traduzindo colunas: {colunas_traduzir}")
    
    for coluna in colunas_traduzir:
        nova_coluna = f"{coluna.replace('_en', '')}_pt"
        valores_traduzidos = []
        
        for valor in df[coluna]:
            try:
                traducao = translator.translate(str(valor))
                valores_traduzidos.append(traducao)
                print(f"  {valor} → {traducao}")
                time.sleep(0.3)  # Pausa para evitar bloqueio
            except Exception as e:
                print(f"  ❌ Erro ao traduzir '{valor}': {e}")
                valores_traduzidos.append(valor)  # Manter original
        
        # Adicionar coluna traduzida
        df[nova_coluna] = valores_traduzidos
    
    print(f"\n✅ DataFrame com traduções:")
    print(df)
    
    return df

def exemplo_traducao_lote_otimizado():
    """Exemplo de tradução otimizada em lotes"""
    print("\n⚡ Exemplo de Tradução Otimizada em Lotes")
    print("=" * 40)
    
    # Lista maior de produtos
    produtos = [
        "Chocolate Chip Cookies", "Vanilla Ice Cream", "Strawberry Yogurt",
        "Grilled Chicken Sandwich", "Caesar Salad", "Beef Burger",
        "French Fries", "Onion Rings", "Fish and Chips", "Pizza Margherita",
        "Spaghetti Carbonara", "Beef Steak", "Salmon Fillet", "Shrimp Scampi",
        "Lobster Bisque", "Clam Chowder", "Oyster Rockefeller", "Crab Cakes",
        "Mussels Marinara", "Scallops Provencal"
    ]
    
    print(f"Total de produtos: {len(produtos)}")
    
    # Inicializar tradutor
    translator = GoogleTranslator(source='en', target='pt')
    
    # Traduzir em lotes de 5
    lote_size = 5
    produtos_traduzidos = []
    
    for i in range(0, len(produtos), lote_size):
        lote = produtos[i:i+lote_size]
        print(f"\n🔄 Traduzindo lote {i//lote_size + 1}: {lote}")
        
        try:
            # Juntar produtos do lote com quebras de linha
            texto_lote = '\n'.join(lote)
            traducao_lote = translator.translate(texto_lote)
            
            # Dividir resultado
            traducoes = traducao_lote.split('\n')
            
            # Adicionar ao resultado
            for j, traducao in enumerate(traducoes):
                if j < len(lote):
                    produtos_traduzidos.append(traducao)
                    print(f"  {lote[j]} → {traducao}")
            
            # Pausa entre lotes
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ Erro no lote: {e}")
            # Em caso de erro, adicionar originais
            produtos_traduzidos.extend(lote)
    
    print(f"\n✅ Tradução em lotes concluída! {len(produtos_traduzidos)} produtos processados")
    return produtos_traduzidos

def exemplo_exportacao():
    """Exemplo de exportação dos resultados"""
    print("\n💾 Exemplo de Exportação")
    print("=" * 40)
    
    # Criar DataFrame com dados traduzidos
    data = {
        'produto_en': ['Apple', 'Banana', 'Orange'],
        'produto_pt': ['Maçã', 'Banana', 'Laranja'],
        'categoria_en': ['Fruit', 'Fruit', 'Fruit'],
        'categoria_pt': ['Fruta', 'Fruta', 'Fruta']
    }
    
    df = pd.DataFrame(data)
    print("DataFrame para exportação:")
    print(df)
    
    # Exportar como CSV
    csv_filename = 'produtos_traduzidos_exemplo.csv'
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    print(f"\n✅ CSV exportado: {csv_filename}")
    
    # Exportar como Excel
    try:
        excel_filename = 'produtos_traduzidos_exemplo.xlsx'
        df.to_excel(excel_filename, index=False)
        print(f"✅ Excel exportado: {excel_filename}")
    except ImportError:
        print("⚠️  Excel não exportado: openpyxl não instalado")
    
    return df

def main():
    """Função principal com todos os exemplos"""
    print("🚀 Tradutor de Dados Universal - Exemplos de Uso")
    print("=" * 60)
    
    try:
        # Executar exemplos
        exemplo_traducao_simples()
        exemplo_traducao_dataframe()
        exemplo_traducao_lote_otimizado()
        exemplo_exportacao()
        
        print("\n🎉 Todos os exemplos executados com sucesso!")
        print("\n💡 Dicas de uso:")
        print("   • Use pausas entre traduções para evitar bloqueios")
        print("   • Traduza em lotes para melhor eficiência")
        print("   • Sempre trate erros de tradução")
        print("   • Exporte resultados em formatos adequados")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução dos exemplos: {e}")
        print("Verifique se todas as dependências estão instaladas:")
        print("  pip install pandas deep-translator openpyxl")

if __name__ == "__main__":
    main()
