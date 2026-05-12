import sqlite3
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# PROJETO: Análise de Gastos Públicos da Prefeitura aplicando Data Science no contexto de Big Data
# EQUIPE: Marcel Gustavo, Marcelo Augusto e João Lucas
# ==========================================

# ==========================================
# 1. SETUP DA BASE DE DADOS LOCAL (ETL)
# ==========================================
print("A criar a base de dados e a popular os dados (com tolerância a falhas)...")
db_path = 'banco_empenhos.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS despesas")
cursor.execute('''
CREATE TABLE despesas (
    empenho TEXT,
    historico TEXT,
    ug TEXT,
    ano TEXT,
    tipo TEXT,
    razao_social TEXT,
    documento TEXT,
    created TEXT,
    valorglobal TEXT,
    valorpago TEXT,
    valorretido TEXT,
    valorliquido TEXT
)
''')

for file_name in ['2024.sql', '2025.sql']:
    file_path = os.path.join('db', file_name)
    if os.path.exists(file_path):
        linhas_sucesso, linhas_erro = 0, 0
        with open(file_path, 'r', encoding='utf-8') as file:
            for linha in file:
                linha = linha.strip()
                if not linha or not linha.startswith('INSERT'): continue
                linha_limpa = linha.replace('`', '').replace("\\'", "''")
                try:
                    cursor.execute(linha_limpa)
                    linhas_sucesso += 1
                except sqlite3.OperationalError:
                    linhas_erro += 1
        print(f"[{file_name}] Inseridos: {linhas_sucesso} | Erros de sintaxe originais ignorados: {linhas_erro}")
    else:
        print(f"ATENÇÃO: Ficheiro {file_path} não encontrado.")

conn.commit()

# ==========================================
# 2. EXTRAÇÃO E LIMPEZA NO PANDAS
# ==========================================
df = pd.read_sql_query("SELECT * FROM despesas", conn)

def limpar_moeda(valor):
    if pd.isna(valor) or valor == '': return 0.0
    valor_limpo = str(valor).replace('R$ ', '').replace('.', '').replace(',', '.')
    return float(valor_limpo)

df['Valor Pago Num'] = df['valorpago'].apply(limpar_moeda)
df['Data Empenho'] = pd.to_datetime(df['ano'], format='%d/%m/%Y', errors='coerce')
df_valido = df.dropna(subset=['Data Empenho']).copy()

# ==========================================
# 3. PROCESSAMENTO MATEMÁTICO (ABC, MMQ e Z-SCORE)
# ==========================================
# --- ETAPA 1: Curva ABC Completa ---
fornecedores = df_valido.groupby('razao_social')['Valor Pago Num'].sum().reset_index()
fornecedores = fornecedores.sort_values(by='Valor Pago Num', ascending=False)
total_gasto = fornecedores['Valor Pago Num'].sum()
fornecedores['Porcentagem (%)'] = (fornecedores['Valor Pago Num'] / total_gasto) * 100
fornecedores['Acumulado (%)'] = fornecedores['Porcentagem (%)'].cumsum()
classe_a = fornecedores[fornecedores['Acumulado (%)'] <= 80]

# --- ETAPA 2: Z-Score Completo (Anomalias) ---
media = df_valido['Valor Pago Num'].mean()
desvio = df_valido['Valor Pago Num'].std()
df_valido['Z-Score'] = (df_valido['Valor Pago Num'] - media) / desvio
anomalias = df_valido[df_valido['Z-Score'] > 3].sort_values(by='Z-Score', ascending=False)

# --- ETAPA 3: MMQ (Tendência) ---
df_valido['Mes_Ano'] = df_valido['Data Empenho'].dt.to_period('M')
gastos_mes = df_valido.groupby('Mes_Ano')['Valor Pago Num'].sum().reset_index()
x = np.arange(len(gastos_mes))
y = gastos_mes['Valor Pago Num'].values
a = np.sum((x - np.mean(x)) * (y - np.mean(y))) / np.sum((x - np.mean(x))**2)
b = np.mean(y) - a * np.mean(x)

# ==========================================
# 4. GERAÇÃO DO RELATÓRIO EXCEL
# ==========================================
print("\nA processar o Big Data e gerar relatório Excel completo...")
nome_arquivo = 'Relatorio_Auditoria_BeloJardim.xlsx'
with pd.ExcelWriter(nome_arquivo) as writer:
    fornecedores.to_excel(writer, sheet_name='Ranking_Fornecedores', index=False)
    anomalias.to_excel(writer, sheet_name='Anomalias_Detectadas', index=False)
print(f"SUCESSO! O ficheiro '{nome_arquivo}' foi criado para auditoria detalhada.")

# ==========================================
# 5. RESUMO EXECUTIVO (TERMINAL TOP 5)
# ==========================================
print("\n" + "="*50)
print("     RESUMO EXECUTIVO PARA APRESENTAÇÃO (TOP 5)")
print("="*50)

print("\n--- ETAPA 1: CURVA ABC (Ouro da base de dados) ---")
print(classe_a[['razao_social', 'Valor Pago Num', 'Acumulado (%)']].head(5).to_string(index=False))

print("\n--- ETAPA 2: TENDÊNCIA COM MMQ ---")
print(f"Equação da Reta ajustada: y = {a:.2f}x + {b:.2f}")

print(f"\n--- ETAPA 3: Z-SCORE (Anomalias Matemáticas) ---")
print(f"Foram detetados {len(anomalias)} pagamentos atípicos (ver excel para lista completa).")
print("Top 5 maiores anomalias (Sinal isolado do ruído):")
print(anomalias[['Data Empenho', 'razao_social', 'Valor Pago Num', 'Z-Score']].head(5).to_string(index=False))

# ==========================================
# 6. VISUALIZAÇÃO GRÁFICA DO MMQ
# ==========================================
plt.figure(figsize=(10, 5))
plt.scatter(x, y, color='blue', label='Gasto Real Mensal', zorder=5)
plt.plot(x, (a * x + b), color='red', linewidth=2, label=f'Tendência MMQ (a={a:.2f})')
plt.title('Tendência dos Gastos da Prefeitura (2024-2025)')
plt.xlabel('Evolução do Tempo (Meses)')
plt.ylabel('Valor Investido (R$)')
plt.ticklabel_format(style='plain', axis='y')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

conn.close()