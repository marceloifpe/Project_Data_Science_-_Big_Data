import sqlite3
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# PROJETO: Banco de Dados II e Data Science
# EQUIPA: Marcel, Marcelo e João Lucas
# ==========================================

# ==========================================
# 1. SETUP DA BASE DE DADOS LOCAL (ETL)
# ==========================================
print("A criar a base de dados e a popular os dados linha a linha (com tolerância a falhas)...")
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

# Ler os ficheiros SQL e executar INSERT linha a linha
for file_name in ['2024.sql', '2025.sql']:
    file_path = os.path.join('db', file_name)
    if os.path.exists(file_path):
        linhas_sucesso = 0
        linhas_erro = 0
        
        with open(file_path, 'r', encoding='utf-8') as file:
            for linha in file:
                linha = linha.strip()
                # Ignorar linhas vazias ou que não sejam comandos de inserção
                if not linha or not linha.startswith('INSERT'):
                    continue
                
                # Tratamento de caracteres incompatíveis entre MySQL e SQLite
                linha_limpa = linha.replace('`', '')
                linha_limpa = linha_limpa.replace("\\'", "''")
                
                # Inserção com tratamento de exceções (Fault Tolerance)
                try:
                    cursor.execute(linha_limpa)
                    linhas_sucesso += 1
                except sqlite3.OperationalError:
                    # Se houver um erro de sintaxe impossível de limpar (ex: aspas não fechadas), ignora esta linha e avança
                    linhas_erro += 1
                    
        print(f"[{file_name}] Concluído: {linhas_sucesso} registos inseridos | {linhas_erro} linhas ignoradas devido a erros de sintaxe.")
    else:
        print(f"ATENÇÃO: Ficheiro {file_path} não encontrado. Verifique a pasta 'db'.")

conn.commit()

# ==========================================
# 2. PIPELINE DE DATA SCIENCE (EXTRAÇÃO)
# ==========================================
print("\nA extrair dados da base de dados para o Pandas...")
df = pd.read_sql_query("SELECT * FROM despesas", conn)

def limpar_moeda(valor):
    if pd.isna(valor) or valor == '': return 0.0
    valor_limpo = str(valor).replace('R$ ', '').replace('.', '').replace(',', '.')
    return float(valor_limpo)

df['Valor Pago Num'] = df['valorpago'].apply(limpar_moeda)
df['Data Empenho'] = pd.to_datetime(df['ano'], format='%d/%m/%Y', errors='coerce')

df_valido = df.dropna(subset=['Data Empenho'])
df_valido = df_valido[df_valido['Valor Pago Num'] > 0].copy()

# ==========================================
# 3. PRINCÍPIO DE PARETO (CURVA ABC)
# ==========================================
print("\n--- ETAPA 1: CURVA ABC (Pareto) ---")
fornecedores = df_valido.groupby('razao_social')['Valor Pago Num'].sum().reset_index()
fornecedores = fornecedores.sort_values(by='Valor Pago Num', ascending=False)

total_gasto = fornecedores['Valor Pago Num'].sum()
fornecedores['Porcentagem (%)'] = (fornecedores['Valor Pago Num'] / total_gasto) * 100
fornecedores['Acumulado (%)'] = fornecedores['Porcentagem (%)'].cumsum()

classe_a = fornecedores[fornecedores['Acumulado (%)'] <= 80]
print("Top 5 Fornecedores que mais receberam recursos:")
print(classe_a[['razao_social', 'Valor Pago Num', 'Acumulado (%)']].head(5).to_string(index=False))

# ==========================================
# 4. MÉTODO DOS MÍNIMOS QUADRADOS (MMQ)
# ==========================================
print("\n--- ETAPA 2: TENDÊNCIA COM MMQ ---")
df_valido['Mes_Ano'] = df_valido['Data Empenho'].dt.to_period('M')
gastos_por_mes = df_valido.groupby('Mes_Ano')['Valor Pago Num'].sum().reset_index()
gastos_por_mes = gastos_por_mes.sort_values('Mes_Ano')

x = np.arange(len(gastos_por_mes))
y = gastos_por_mes['Valor Pago Num'].values

media_x, media_y = np.mean(x), np.mean(y)
a = np.sum((x - media_x) * (y - media_y)) / np.sum((x - media_x)**2)
b = media_y - (a * media_x)
y_tendencia = a * x + b

print(f"Equação da Reta ajustada: y = {a:.2f}x + {b:.2f}")

# ==========================================
# 5. DETEÇÃO DE ANOMALIAS (Z-SCORE)
# ==========================================
print("\n--- ETAPA 3: Z-SCORE (ANOMALIAS MATEMÁTICAS) ---")
media_empenhos = df_valido['Valor Pago Num'].mean()
desvio_empenhos = df_valido['Valor Pago Num'].std()

df_valido['Z-Score'] = (df_valido['Valor Pago Num'] - media_empenhos) / desvio_empenhos
anomalias = df_valido[df_valido['Z-Score'] > 3].sort_values(by='Z-Score', ascending=False)

print(f"Foram detetados {len(anomalias)} pagamentos atípicos (3 desvios padrões acima da média).")
print("Top 5 anomalias detetadas:")
print(anomalias[['Data Empenho', 'razao_social', 'Valor Pago Num', 'Z-Score']].head(5).to_string(index=False))

# ==========================================
# 6. VISUALIZAÇÃO GRÁFICA DO MMQ
# ==========================================
plt.figure(figsize=(10, 5))
plt.scatter(x, y, color='blue', label='Gasto Mensal Real', zorder=5)
plt.plot(x, y_tendencia, color='red', linewidth=2, label=f'Tendência MMQ (a={a:.2f})')
plt.title('Tendência dos Gastos da Prefeitura (2024-2025)')
plt.xlabel('Evolução do Tempo (Meses)')
plt.ylabel('Valor Investido (R$)')
plt.ticklabel_format(style='plain', axis='y')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# Fechar a ligação
conn.close()