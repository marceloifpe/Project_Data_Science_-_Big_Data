# 📊 Data Science & Big Data — Análise de Despesas Públicas
### Prefeitura Municipal de Belo Jardim · Biênio 2024–2025

<div align="center">

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge&logo=python&logoColor=white)

</div>

---

## 🏫 Informações Acadêmicas

| Campo | Detalhe |
|---|---|
| **Instituição** | Instituto Federal de Pernambuco — IFPE |
| **Campus** | Belo Jardim |
| **Curso** | Engenharia de Software |
| **Disciplina** | Banco de Dados II |
| **Professor** | Almir Moura |
| **Período** | 2025 |

**Equipe:**

| 👤 | Nome |
|---|---|
| 🎓 | João Lucas |
| 🎓 | Marcel Gustavo |
| 🎓 | Marcelo Augusto de Barros Araújo |

---

## 📌 Sobre o Projeto

O município de Belo Jardim — PE, mesmo sendo cidade de médio porte, gera um alto volume de dados financeiros a nível de Big Data diariamente. A fiscalização manual de milhares de empenhos é inviável.

O desafio do biênio 2024–2025 **não é a falta de dados**, mas a ausência de inteligência analítica para:

- 🔍 Cruzar informações entre fornecedores e contratos
- 📈 Prever tendências de gastos com dinheiro público
- 🚨 Detectar anomalias financeiras automaticamente

Este projeto aplica um **pipeline completo de Data Science** — da ingestão bruta dos dados até a geração de relatórios — sobre dados reais e públicos extraídos do portal de transparência da prefeitura.

---

## 🗂️ Estrutura do Repositório

```
📦 projeto-data-science-belo-jardim
├── 📁 db/
│   ├── 2024.sql                  # Empenhos do exercício 2024
│   └── 2025.sql                  # Empenhos do exercício 2025
├── 📄 main.py                    # Script principal (ETL + Análises + Relatório)
├── 📊 banco_empenhos.db          # Banco SQLite gerado pelo script
├── 📑 Relatorio_Auditoria_BeloJardim.xlsx  # Relatório Excel gerado
└── 📄 README.md
```

---

## 🔄 Pipeline do Projeto

```
Fontes de Dados
  2024.sql ──┐
             ├──► ETL (sqlite3) ──► banco_empenhos.db ──► Pandas + NumPy
  2025.sql ──┘         │                                        │
              tolerância a erros                     ┌──────────┼──────────┐
              de sintaxe SQL                         │          │          │
                                                 Curva    Z-Score        MMQ
                                                  ABC    anomalias   tendência
                                                     │          │          │
                                                     └──────────┼──────────┘
                                                                │
                                              ┌─────────────────┴──────────────┐
                                         Excel (.xlsx)              Gráfico (Matplotlib)
                                    Ranking + Anomalias           Scatter + Reta de tendência
```

---

## ⚙️ Tecnologias Utilizadas

### `sqlite3` — Banco de Dados Local
- Biblioteca **padrão do Python**, sem instalação de servidor externo
- Criação e população da tabela `despesas` via arquivos `.sql`
- Escolhido por portabilidade: o banco é um único arquivo `.db`, executável em qualquer máquina

### `os` — Sistema de Arquivos
- Verificação defensiva da existência dos arquivos SQL antes da leitura
- Evita `FileNotFoundError` em ambientes com estrutura de pasta diferente

### `Pandas` — Processamento e Análise de Dados
- Leitura do banco SQLite direto para DataFrame via `pd.read_sql_query`
- Limpeza de valores monetários no padrão brasileiro (`R$ 1.234,56` → `float`)
- Conversão de datas, agrupamentos, cálculo de percentuais e soma acumulada
- Geração do relatório Excel com múltiplas abas via `pd.ExcelWriter`

### `NumPy` — Matemática Vetorial
- Implementação manual do **MMQ (Método dos Mínimos Quadrados)**
- Operações de somatório e média sobre arrays para cálculo dos coeficientes `a` e `b` da reta de tendência

### `Matplotlib` — Visualização
- Gráfico de dispersão dos gastos mensais reais (pontos azuis)
- Sobreposição da reta de tendência do MMQ (linha vermelha)
- Configurado para exibir valores do eixo Y sem notação científica

---

## 🧮 Modelagem Matemática e Estatística

### 📊 Curva ABC — Princípio de Pareto
Classifica fornecedores por participação no total pago:

```
Fornecedores ordenados (maior → menor valor)
  → Calcula participação % de cada um no total
  → Acumula progressivamente (cumsum)
  → Classe A = fornecedores até 80% acumulado
```

> Resultado: poucos fornecedores concentram a maior parte do orçamento — foco prioritário de auditoria.

### 📉 MMQ — Mínimos Quadrados (Regressão Linear)
Encontra a reta `y = ax + b` que melhor se ajusta à série temporal de gastos mensais:

```
         Σ (xᵢ - x̄)(yᵢ - ȳ)
a = ─────────────────────────      b = ȳ - a·x̄
         Σ (xᵢ - x̄)²
```

- `a > 0` → gastos crescendo ao longo do tempo
- `a < 0` → gastos decrescendo
- `a ≈ 0` → sem tendência significativa

### 🚨 Z-Score — Detecção de Anomalias
Identifica pagamentos estatisticamente atípicos:

```
         (valor - média)
Z = ─────────────────────
          desvio padrão
```

> Valores com **Z > 3** estão no 0,3% mais extremo da distribuição — sinalizados para investigação.

---

## 🛠️ Como Executar

### Pré-requisitos

```bash
pip install pandas numpy matplotlib openpyxl
```

### Estrutura de Pastas Esperada

```
projeto/
├── db/
│   ├── 2024.sql
│   └── 2025.sql
└── main.py
```

### Executar

```bash
python main.py
```

### Saídas Geradas

| Arquivo | Conteúdo |
|---|---|
| `banco_empenhos.db` | Banco SQLite com 6.051 registros de empenhos |
| `Relatorio_Auditoria_BeloJardim.xlsx` | Aba **Ranking_Fornecedores** (Curva ABC) + aba **Anomalias_Detectadas** (Z-Score) |
| Gráfico (janela) | Scatter dos gastos mensais + reta de tendência do MMQ |

---

## 📈 Resultados Obtidos

### Base de Dados

| Indicador | Valor |
|---|---|
| Total de registros carregados | **6.051** |
| Empenhos de 2024 | 3.074 |
| Empenhos de 2025 | 3.002 |
| Erros de sintaxe SQL (ignorados) | 14 |
| Tipos de empenho | Ordinário · Global · Estimativa |
| CPFs mascarados | 1.866 |
| Empenhos não quitados (pago = R$ 0,00) | 698 |

### Top 5 Fornecedores — Curva ABC

| # | Fornecedor | Total Pago | Acumulado |
|---|---|---|---|
| 1° | Município de Belo Jardim – Imp. Restos a Pagar | R$ 142.392.856,82 | 39,19% |
| 2° | Belo Jardim Prev – Benefícios Previdenciários | R$ 24.724.323,86 | 46,00% |
| 3° | INSS | R$ 15.362.724,59 | 50,23% |
| 4° | Vale Bento Transporte Escolar | R$ 12.434.893,72 | 53,65% |
| 5° | C3 Engenharia Ltda | R$ 11.978.854,87 | 56,95% |

### Top 3 Anomalias — Z-Score

| Z-Score | Empenho | Valor Pago | Contexto |
|---|---|---|---|
| 33,22 | 92/2025 | R$ 14.311.173,77 | Folha de servidores efetivos |
| 32,47 | 111/2024 | R$ 13.986.572,74 | Folha de servidores efetivos |
| 27,13 | 101/2025 | R$ 11.697.234,26 | Folha de servidores efetivos |

> ℹ️ As maiores anomalias são pagamentos de folha salarial — valores altos esperados por natureza, mas matematicamente atípicos frente à média dos demais empenhos. Isso reforça que o Z-Score deve ser sempre interpretado com contexto de domínio.

---

## ⚠️ Tratamentos Aplicados nos Dados SQL

| Problema encontrado | Causa | Solução aplicada |
|---|---|---|
| **Crases nos nomes de colunas** | Sintaxe MySQL incompatível com SQLite | `linha.replace('`', '')` |
| **Aspas duplas dentro do histórico** | Nomes de eventos entre aspas no texto | `try/except OperationalError` — linha ignorada |
| **Campo `ano` com nome enganoso** | Contém data completa `dd/mm/yyyy`, não só o ano | `pd.to_datetime(format='%d/%m/%Y')` |
| **Valores monetários como texto** | Formato `R$ 1.234,56` não é número | Função `limpar_moeda()` com 3 substituições em cascata |
| **CPFs mascarados** | Privacidade de pessoas físicas (`***.***.004-53`) | Armazenados como estão; análises por `razao_social` |
| **698 empenhos com `valorpago = R$ 0,00`** | Empenhos reservados mas não quitados | Registrados normalmente; limitação declarada no Z-Score |

---

## 🎯 Conexão com Big Data — Os 5 Vs

| V | Como o projeto atende |
|---|---|
| **Volume** | 6.051 registros reais de empenhos, inviáveis de analisar manualmente |
| **Variedade** | Texto livre, datas, valores monetários, CPFs/CNPJs, categorias |
| **Velocidade** | Pipeline ETL automatizado — do arquivo bruto ao relatório em segundos |
| **Veracidade** | Fonte oficial (portal de transparência) + tratamento de qualidade de dados |
| **Valor** | ABC prioriza auditoria · Z-Score detecta anomalias · MMQ projeta tendências |

---

## 📚 Referências

- Gartner (2026). *Principais Previsões para Data Analytics 2026*. Disponível em: [bluestudio.estadao.com.br](https://bluestudio.estadao.com.br/agencia-de-comunicacao/prnewswire/gartner-aponta-as-principais-previsoes-para-data-analytics-em-2026/)
- Business Research Insights. *Data Analytics Market Report*. Disponível em: [businessresearchinsights.com](https://www.businessresearchinsights.com/pt/market-reports/data-analytics-market-108876)
- Dama International (2017). *DAMA-DMBOK: Data Management Body of Knowledge*, 2ª ed.
- Apache Foundation. *Apache Spark Documentation*. Disponível em: [spark.apache.org](https://spark.apache.org)
- Scikit-learn. *Machine Learning in Python*. Disponível em: [scikit-learn.org](https://scikit-learn.org)

---

## 📄 Licença

Projeto acadêmico desenvolvido para fins educacionais. Os dados utilizados são públicos, extraídos do Portal de Transparência da Prefeitura Municipal de Belo Jardim — PE.

---

<div align="center">

**IFPE · Campus Belo Jardim · Engenharia de Software · Banco de Dados II**

*Prof. Almir Moura · 2025*

</div>