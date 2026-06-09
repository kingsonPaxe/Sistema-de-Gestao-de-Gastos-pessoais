# 🇦🇴 ADAPTAÇÃO PARA ANGOLA - Sistema de Gestão de Gastos Pessoais

## 📋 Resumo das Alterações

Este documento descreve todas as mudanças realizadas para adaptar o sistema de gestão financeira pessoal para o contexto angolano, incluindo:

- ✅ Moeda: Kwanza (Kz) em lugar de Real Brasileiro (R$)
- ✅ Formatação Numérica: Estilo europeu (pontos para milhares, vírgula para decimais)
- ✅ Categorias: Angolanas específicas para receitas e despesas
- ✅ Terminologia: Português angolano
- ✅ Data: Formato dd/mm/aaaa
- ✅ Indicadores: Taxa de poupança e evolução mensal
- ✅ Relatórios: Formatação em Kwanza

---

## 🔄 ARQUIVOS MODIFICADOS

### 1. **NOVO: `utils/currency.py`**
- **Criação**: Novo módulo centralizado para formatação de moeda
- **Funções principais**:
  - `format_kwanza(value)` → "Kz 1.500,00"
  - `parse_kwanza(value)` → Converte string para Decimal
  - `kwanza_filter()` → Filtro Jinja para templates
  - `date_filter()` → Filtro Jinja para datas (dd/mm/yyyy)

**Exemplo de uso:**
```python
from utils.currency import format_kwanza
valor = format_kwanza(1500)  # "Kz 1.500,00"
```

**Em templates:**
```jinja
{{ balance|kwanza }}
{{ transaction.date|format_date }}
```

---

### 2. **MODIFICADO: `models/income.py`**

**Mudanças:**
```python
# ANTES
amount = db.Column(db.Numeric(10, 2), nullable=False)
def __repr__(self):
    return f'<Income {self.title} R${self.amount}>'

# DEPOIS
from decimal import Decimal
amount = db.Column(db.Numeric(12, 2), nullable=False)  # Maior precisão
def __repr__(self):
    return f'<Income {self.title} Kz{self.amount}>'
```

**to_dict() method:**
- Data agora em formato `'%d/%m/%Y'` ao invés de `'%Y-%m-%d'`
- Mantém precisão com Decimal internamente

---

### 3. **MODIFICADO: `models/expense.py`**

**Mesmas mudanças que Income:**
- Numeric(12, 2) para melhor precisão
- __repr__ atualizado para Kz
- to_dict() com formato de data angolano

---

### 4. **MODIFICADO: `app.py`**

**Mudanças principais:**
```python
# NOVO: Importação do módulo de moeda
from utils.currency import kwanza_filter, date_filter

# NOVO: Registrar filtros Jinja
app.jinja_env.filters['kwanza'] = kwanza_filter
app.jinja_env.filters['format_date'] = date_filter

# NOVO: Função _seed_default_categories() com categorias angolanas
```

**Categorias de Receita (7 novas):**
- Salário
- Negócio
- Freelance
- Comissão
- Bónus
- Investimentos
- Outros

**Categorias de Despesa (15 novas):**
- Alimentação
- Táxi
- Transporte
- Combustível
- ENDE (Eletricidade)
- EPAL (Água)
- Internet
- Unitel (Operadora de Telefonia)
- Africell (Operadora de Telefonia)
- Movicel (Operadora de Telefonia)
- Educação
- Saúde
- Habitação
- Renda
- Impostos
- Outros

---

### 5. **MODIFICADO: `routes/dashboard.py`**

**Novo cálculo de indicadores:**

```python
# NOVO: Cálculo de receitas/despesas do mês
monthly_income = sum of transactions in current month
monthly_expense = sum of expenses in current month

# NOVO: Taxa de poupança
savings_rate = (monthly_savings / monthly_income) * 100

# NOVO: Economia do mês
monthly_savings = monthly_income - monthly_expense
```

**Contexto passado ao template agora inclui:**
- `monthly_income`
- `monthly_expense`
- `monthly_savings`
- `savings_rate`

---

### 6. **MODIFICADO: `templates/base.html`**

```html
<!-- ANTES -->
<html lang="pt-BR">
<meta name="description" content="...">

<!-- DEPOIS -->
<html lang="pt-AO">
<meta name="description" content="Sistema de Gestão de Gastos Pessoais - Controle suas finanças em Kwanza de forma simples e intuitiva">
```

---

### 7. **MODIFICADO: `templates/dashboard.html`**

**Labels atualizados:**
```
ANTES → DEPOIS
────────────────
"Saldo Atual" → "Saldo Disponível"
"Total de Receitas" → "Receitas do Mês"
"Total de Despesas" → "Despesas do Mês"
```

**Novo card adicionado:**
```html
<!-- Taxa de Poupança -->
<div class="stat-card stat-card--savings">
    <span class="stat-card__label">Taxa de Poupança</span>
    <span class="stat-card__value">{{ "%.1f"|format(savings_rate) }}%</span>
    <span class="text-muted small">{{ monthly_savings|kwanza }}</span>
</div>
```

**Uso do filtro Kwanza:**
```jinja
<!-- ANTES -->
R$ {{ '{:,.2f}'.format(balance) }}

<!-- DEPOIS -->
{{ balance|kwanza }}
```

**Data com filtro:**
```jinja
<!-- ANTES -->
{{ t.date.strftime('%d/%m/%Y') }}

<!-- DEPOIS -->
{{ t.date|format_date }}
```

---

### 8. **MODIFICADO: `templates/incomes.html`**

**Mudanças:**
- Label: "Valor (R$)" → "Valor (Kz)"
- Formatação: `R$ {{ '{:,.2f}'.format(income.amount) }}` → `{{ income.amount|kwanza }}`

---

### 9. **MODIFICADO: `templates/expenses.html`**

**Mesmas mudanças que incomes.html**

---

### 10. **MODIFICADO: `templates/profile.html`**

```jinja
<!-- ANTES -->
{{ current_user.created_at.strftime('%B de %Y') }}

<!-- DEPOIS -->
{{ current_user.created_at|format_date('%d/%m/%Y') }}
```

---

### 11. **MODIFICADO: `static/js/dashboard.js`**

**Nova função de formatação:**
```javascript
function formatCurrency(value) {
    return Number(value).toLocaleString('pt-AO', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
        useGrouping: true
    });
}

function formatKwanza(value) {
    return 'Kz ' + formatCurrency(value);
}
```

**Atualizações nos charts:**
- Pie Chart tooltip: `Kz {{ formatCurrency(ctx.parsed) }}`
- Bar Chart y-axis: `Kz {{ formatCurrency(v) }}`
- Legend: "Receitas" e "Despesas" (já em português)

---

### 12. **MODIFICADO: `services/report_service.py`**

**Importação nova:**
```python
from utils.currency import format_kwanza
```

**Mudanças no PDF:**
- Título: "Sistema de Gestão de Gastos Pessoais - Angola"
- Todos os valores: `format_kwanza()` em lugar de formatação manual com R$
- Footer: Menciona "Angola"

**Exemplo:**
```python
# ANTES
f"R$ {total_income:,.2f}"

# DEPOIS
format_kwanza(total_income)
```

---

## 📊 EXEMPLOS DE FORMATAÇÃO

### Kwanza
```
1500        → Kz 1.500,00
25000       → Kz 25.000,00
1250000.75  → Kz 1.250.000,75
0.50        → Kz 0,50
```

### Datas
```
2026-06-08  → 08/06/2026
2026-01-15  → 15/01/2026
```

---

## 🔧 TECNOLOGIAS UTILIZADAS

### Backend
- **Python 3.11+**
- **Flask 3.0**
- **SQLAlchemy 2.0** (Decimal para precisão financeira)
- **ReportLab 4** (PDF com Kwanza)

### Frontend
- **Jinja2** (Filtros customizados)
- **Chart.js 4** (Gráficos com Kz)
- **JavaScript ES6** (Formatação locale)

### Banco de Dados
- **Numeric(12, 2)** para todas as colunas monetárias
- Suporta até 1 trilião de Kwanza

---

## 🚀 COMO USAR

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Executar aplicação
```bash
python app.py
```

### 3. Acessar em template (Kwanza)
```jinja
{{ valor|kwanza }}
<!-- Resultado: Kz 1.500,00 -->
```

### 4. Acessar em template (Data)
```jinja
{{ data|format_date }}
<!-- Resultado: 08/06/2026 -->
```

### 5. Usar em Python
```python
from utils.currency import format_kwanza, parse_kwanza

# Formatar
print(format_kwanza(1500))  # "Kz 1.500,00"

# Parser
valor = parse_kwanza("Kz 1.500,00")  # Decimal('1500.00')
```

---

## 📈 NOVOS INDICADORES

### Dashboard Principal
- **Saldo Disponível**: Total de receitas - despesas
- **Receitas do Mês**: Soma de todas receitas do mês atual
- **Despesas do Mês**: Soma de todas despesas do mês atual
- **Taxa de Poupança**: % do income poupado este mês
- **Transações**: Total de registros (receitas + despesas)

### Gráficos
- **Pie Chart**: Distribuição de despesas por categoria (em Kz)
- **Bar Chart**: Receitas vs Despesas por mês (em Kz)

### Relatórios PDF
- Período customizável
- Resumo financeiro em Kz
- Tabelas detalhadas (receitas e despesas)
- Totalizações por período

---

## 🔐 SEGURANÇA

- ✅ Decimal (12,2) previne problemas de arredondamento
- ✅ Validação de entrada em todos endpoints
- ✅ Proteção CSRF
- ✅ Autenticação requerida em dashboard
- ✅ Isolamento de dados por usuário

---

## 📝 NOMENCLATURA ANGOLANA

| Termo | Português BR | Português AO |
|-------|-------------|-------------|
| Moeda | Real (R$) | Kwanza (Kz) |
| Aluguel | Aluguel | Renda da Casa |
| Táxi/Uber | Mobilidade | Táxi |
| Energia | Luz | ENDE |
| Água | Água | EPAL |
| Operadora | Vivo, Claro | Unitel, Africell, Movicel |
| Bônus | Bônus | Bónus |

---

## 🔄 FLUXO DE DADOS

```
Entrada do Usuário (float)
         ↓
Routes (income.py, expense.py)
         ↓
Banco de Dados (Numeric 12,2)
         ↓
Modelo (Decimal)
         ↓
Template/API (Jinja Filter kwanza)
         ↓
Exibição Final (Kz 1.500,00)
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

- [x] Moeda substituída em todos templates
- [x] Formato numérico europeu (. para milhares, , para decimais)
- [x] Categorias angolanas criadas
- [x] Filtros Jinja registrados
- [x] Dashboard mostra valores mensais
- [x] Charts formatados em Kz
- [x] Relatórios em Kwanza
- [x] Datas em dd/mm/yyyy
- [x] Modelos usam Decimal(12,2)
- [x] Nomenclatura angolana aplicada

---

## 🎯 MELHORIAS FUTURAS ESPECÍFICAS PARA ANGOLA

1. **Integração Bancária**: Conexão com bancos angolanos (BCI, BAI, Banco de Desenvolvimento)
2. **SMS Notifications**: Alertas via operadoras locais (Unitel, Africell, Movicel)
3. **Conversão Multi-Moeda**: USD, EUR para Kwanza (com taxas do BNA)
4. **Impostos Locais**: Cálculo de IVA (17%) e outros impostos angolanos
5. **Relatórios Tributários**: Para Autoridade Tributária Angolana
6. **Exportação Excel**: Compatível com software local
7. **Análise Regional**: Gastos por província
8. **Budgeting Avançado**: Planejamento em Kz com metas mensais

---

## 📞 SUPORTE

Para dúvidas sobre a adaptação angolana, consultar:
- Documentação: [README.md](README.md)
- Código de Moeda: [utils/currency.py](utils/currency.py)
- Exemplo de Uso: [templates/dashboard.html](templates/dashboard.html)

---

**Data de Adaptação**: 08 de Junho de 2026  
**Versão**: 2.0 (Angola)  
**Status**: ✅ Produção Pronta
