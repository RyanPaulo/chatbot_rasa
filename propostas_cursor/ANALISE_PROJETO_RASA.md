# 📊 ANÁLISE COMPLETA DO CHATBOT RASA

## 1. 🎯 OPORTUNIDADES DE MELHORIA NA NLU

### 1.1 Análise do `data/nlu.yml`

#### ✅ **Pontos Fortes:**
- Boa cobertura de intents básicos (saudar, despedir, agradecer)
- Uso adequado de lookup tables para disciplinas e docentes
- Sinônimos bem definidos para disciplinas comuns (SD, ES, BD, etc.)

#### ⚠️ **Problemas Identificados:**

**A) Distribuição Desequilibrada de Exemplos:**
- `solicitar_atendimento_docente`: **9 exemplos** (bem coberto)
- `solicitar_info_docente`: **2 exemplos** (insuficiente!)
- `consultar_data_avaliacao`: **2 exemplos** (insuficiente!)
- `consultar_horario_aula`: **2 exemplos** (insuficiente!)
- `consultar_aviso`: **8 exemplos** (bom)
- `solicitar_material_aula`: **13 exemplos** (bom, mas tem duplicatas)

**B) Exemplos Duplicados:**
```yaml
# Linhas 112 e 116 são idênticas:
- vc consegue me mandar esse material?
# Linhas 115 e 117 são muito similares:
- me manda o material de [cloud computing]{"entity": "disciplina"}
- pode me enviar o material de [cloud computing]{"entity": "disciplina"}?
```

**C) Exemplos com Problemas:**
- Linha 104: `- o que e cocomo 81` - **Falta anotação de entidade** (`topico_estudo`)
- Linha 56: `- qual a sala da aula de hoje` - **Falta entidade `disciplina`** (deveria ser obrigatória)
- Linha 89: `- atendimento da coordenacao` - **Falta entidade `nome_docente`** (mas pode ser intencional)

**D) Falta de Variação Linguística:**
- Muitos exemplos são muito similares entre si
- Poucas variações de estilo (formal vs. informal)
- Falta de exemplos com erros de digitação comuns

**E) Lookup Tables com Problemas:**
- `disciplina` lookup tem **duplicatas** (linhas 147 e 171: "Qualidade de Software")
- Linha 160: `ClP` parece ser um erro de digitação (deveria ser "CLP"?)
- Linha 169: `Gestao` sem acento (inconsistente com outras entradas)

#### 📝 **Recomendações:**

1. **Adicionar mais exemplos para intents sub-representados:**
   ```yaml
   - intent: solicitar_info_docente
     examples: |
       - qual o email do professor [Zezinho]{"entity": "nome_docente"}
       - como falo com a coordenadora [Eliane]{"entity": "nome_docente"}
       - preciso do contato do [Alvaro]{"entity": "nome_docente"}
       - email da [Myriam]{"entity": "nome_docente"}
       - qual a sala do [Hugo]{"entity": "nome_docente"}
       - onde encontro o [Magrini]{"entity": "nome_docente"}
       - contato do professor [Zezinho]{"entity": "nome_docente"}
       - me passa o email do [Alvaro]{"entity": "nome_docente"}
   ```

2. **Adicionar variações com erros comuns:**
   ```yaml
   - quando e a [NP1]{"entity": "tipo_avaliacao"} de [engenharia de software]{"entity": "disciplina"}
   - quando e a [np1]{"entity": "tipo_avaliacao"} de [ES]{"entity": "disciplina"}
   - data da [prova 1]{"entity": "tipo_avaliacao"} de [engenharia]{"entity": "disciplina"}
   ```

3. **Remover duplicatas e corrigir erros**

### 1.2 Análise do `domain.yml`

#### ✅ **Pontos Fortes:**
- Estrutura bem organizada
- Slots com `influence_conversation: true` (correto)
- Mapeamentos de slots bem definidos

#### ⚠️ **Problemas Identificados:**

**A) Conflito Potencial entre Intents:**
- `solicitar_info_docente` vs `solicitar_atendimento_docente`
  - **RISCO:** Ambos lidam com informações de docentes
  - **PROBLEMA:** Exemplos podem ser confundidos pelo classificador
  - **SOLUÇÃO:** Tornar os exemplos mais distintos:
    - `solicitar_info_docente`: foco em **contato** (email, sala)
    - `solicitar_atendimento_docente`: foco em **horário de atendimento**

**B) Entidade `topico_estudo` não tem slot:**
- A entidade é extraída mas não é armazenada em slot
- Isso pode ser intencional (usado apenas na action), mas pode ser útil ter um slot

**C) Falta de validação de slots:**
- Não há `action_validate_*` para validar se `disciplina` ou `nome_docente` são válidos antes de chamar a API

#### 📝 **Recomendações:**

1. **Adicionar slots para entidades importantes:**
   ```yaml
   topico_estudo:
     type: text
     influence_conversation: false
     mappings:
     - type: from_entity
       entity: topico_estudo
   ```

2. **Criar actions de validação** (ver seção 2.2)

### 1.3 Análise do `config.yml`

#### ✅ **Pontos Fortes:**
- Pipeline adequado para português
- Uso de `DIETClassifier` (bom para português)
- `EntitySynonymMapper` configurado (essencial para sinônimos)

#### ⚠️ **Problemas Identificados:**

**A) Tokenizer Inadequado:**
- `WhitespaceTokenizer` **não é ideal para português**
- Português tem palavras compostas e acentuação
- **RECOMENDAÇÃO:** Usar `JiebaTokenizer` (suporta português) ou `SpacyTokenizer`

**B) Falta de Componente de Língua:**
- Não há componente específico para português (ex: `SpacyNLP` com modelo pt)
- Isso pode melhorar a extração de entidades

**C) Threshold do FallbackClassifier:**
- `threshold: 0.3` pode ser muito baixo (muitos falsos positivos)
- `ambiguity_threshold: 0.1` também pode ser ajustado

#### 📝 **Recomendações:**

```yaml
pipeline:
  - name: SpacyNLP
    model: "pt_core_news_sm"  # Requer: python -m spacy download pt_core_news_sm
  - name: SpacyTokenizer
  - name: SpacyFeaturizer
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 4
  - name: DIETClassifier
    epochs: 100
    constrain_similarities: true
  - name: EntitySynonymMapper
  - name: ResponseSelector
    epochs: 100
    constrain_similarities: true
  - name: FallbackClassifier
    threshold: 0.4  # Aumentado de 0.3
    ambiguity_threshold: 0.15  # Aumentado de 0.1
```

**NOTA:** Se não quiser usar Spacy, mantenha o pipeline atual mas considere aumentar os thresholds.

---

## 2. 🔧 OTIMIZAÇÕES NA LÓGICA

### 2.1 Análise do `actions/actions.py`

#### ✅ **Pontos Fortes:**
- Separação clara de responsabilidades
- Todas as actions fazem apenas chamadas HTTP (conforme arquitetura)
- Tratamento de erros presente

#### ⚠️ **Problemas Identificados:**

**A) Função `get_disciplina_id_by_name` Redundante:**
- Esta função é chamada em **múltiplas actions** (ActionBuscarCronograma, ActionBuscarDataAvaliacao, ActionBuscarMaterial)
- **OPORTUNIDADE:** Criar uma classe base ou helper para evitar duplicação

**B) Tratamento de Erros Inconsistente:**
- Algumas actions usam `response.raise_for_status()`
- Outras usam `if response.ok:`
- **PROBLEMA:** Comportamento inconsistente pode levar a bugs

**C) Falta de Timeout nas Requisições:**
- `requests.get/post` sem timeout pode travar o bot
- **RISCO:** Se a API FastAPI estiver lenta, o bot fica travado

**D) URL da API com Typo:**
- Linha 17: `/disciplinas/get_diciplina_id/` - **"diciplina" está errado!** (deveria ser "disciplina")
- Isso pode causar 404 se a API estiver correta

**E) Lógica de Busca de Docente Duplicada:**
- `ActionBuscarAtendimentoDocente` e `ActionBuscarInfoDocente` têm lógica similar
- Ambos fazem busca por nome parcial (`if nome_docente.lower() in doc.get('nome_professor', '').lower()`)
- **OPORTUNIDADE:** Extrair para função helper

**F) Slot não limpo em alguns casos:**
- `ActionBuscarAtendimentoDocente` limpa o slot no final (linha 219)
- Mas se houver erro antes (linha 217), o slot não é limpo
- **RISCO:** Slot pode ficar "preso" em caso de erro

#### 📝 **Recomendações:**

1. **Criar classe helper para requisições:**
```python
class APIHelper:
    API_URL = "http://127.0.0.1:8000"
    TIMEOUT = 10  # segundos
    
    @staticmethod
    def get_disciplina_id(disciplina_nome: str) -> str | None:
        try:
            response = requests.get(
                f"{APIHelper.API_URL}/disciplinas/get_disciplina_id/{disciplina_nome}",
                timeout=APIHelper.TIMEOUT
            )
            response.raise_for_status()
            return response.json().get("id_disciplina")
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def buscar_docente_por_nome(nome: str) -> dict | None:
        # Lógica unificada para buscar docente
        pass
```

2. **Adicionar timeout em todas as requisições:**
```python
response = requests.get(url, timeout=10)
```

3. **Corrigir typo na URL** (linha 17)

4. **Usar try/finally para garantir limpeza de slots:**
```python
def run(self, ...):
    try:
        # lógica
    finally:
        return [SlotSet("nome_docente", None)]
```

### 2.2 Análise do `data/rules.yml`

#### ✅ **Pontos Fortes:**
- Regras bem estruturadas
- Formulários configurados corretamente
- Uso adequado de `active_loop` e `slot_was_set`

#### ⚠️ **Problemas Identificados:**

**A) Regra de Fallback pode não funcionar:**
- Linha 109: `intent: nlu_fallback`
- **PROBLEMA:** O Rasa 3.x usa `nlu_fallback` apenas quando o FallbackClassifier é acionado
- Se o threshold for muito baixo, pode não ser acionado
- **SOLUÇÃO:** Verificar se o threshold está adequado (já mencionado na seção 1.3)

**B) Falta de Regra para `informar_disciplina`:**
- O intent `informar_disciplina` existe no domain.yml
- Mas não há regra que o utilize
- **PROBLEMA:** Se o usuário apenas digitar "Cloud Computing", o bot não saberá o que fazer

**C) Formulários podem ficar "presos":**
- Se o usuário não responder à pergunta do formulário, ele fica ativo indefinidamente
- **FALTA:** Regra para cancelar formulário (ex: se usuário digitar "cancelar")

**D) Regras de Formulário podem conflitar:**
- As regras de ativação de formulário verificam `slot_was_set: null`
- Mas se o slot já estiver preenchido de uma conversa anterior, o formulário não será ativado
- Isso pode ser intencional, mas pode confundir o usuário

#### 📝 **Recomendações:**

1. **Adicionar regra para cancelar formulários:**
```yaml
- rule: Cancelar formulario de atendimento
  condition:
  - active_loop: form_atendimento_docente
  steps:
  - intent: despedir
  - action: action_deactivate_loop
  - active_loop: null
  - action: utter_agradecer
```

2. **Adicionar regra para `informar_disciplina`:**
```yaml
- rule: Usuario informa disciplina diretamente
  steps:
  - intent: informar_disciplina
  - action: action_buscar_material  # ou outra action apropriada
```

3. **Adicionar validação de slots nos formulários:**
- Criar `ActionValidateFormAtendimentoDocente` e `ActionValidateFormBuscarMaterial`

---

## 3. 🐛 ERROS CRÍTICOS

### 3.1 Erros de Sintaxe YAML

✅ **Nenhum erro de sintaxe encontrado** - Todos os arquivos YAML estão bem formatados.

### 3.2 Erros de Lógica RASA

#### ❌ **ERRO CRÍTICO 1: Typo na URL da API**
- **Arquivo:** `actions/actions.py`, linha 17
- **Problema:** `/disciplinas/get_diciplina_id/` (deveria ser "disciplina")
- **Impacto:** Pode causar 404 se a API estiver correta
- **Severidade:** ALTA

#### ❌ **ERRO CRÍTICO 2: Exemplo sem anotação de entidade**
- **Arquivo:** `data/nlu.yml`, linha 104
- **Problema:** `- o que e cocomo 81` (falta `{"entity": "topico_estudo"}`)
- **Impacto:** O modelo não aprenderá a extrair "cocomo 81" como entidade
- **Severidade:** MÉDIA

#### ⚠️ **ERRO CRÍTICO 3: Duplicatas no lookup de disciplinas**
- **Arquivo:** `data/nlu.yml`, linhas 147 e 171
- **Problema:** "Qualidade de Software" aparece duas vezes
- **Impacto:** Pode confundir o modelo (baixo impacto, mas é má prática)
- **Severidade:** BAIXA

#### ⚠️ **ERRO CRÍTICO 4: Exemplos duplicados**
- **Arquivo:** `data/nlu.yml`, linhas 112 e 116
- **Problema:** `- vc consegue me mandar esse material?` aparece duas vezes
- **Impacto:** Overfitting dessa frase específica
- **Severidade:** BAIXA

### 3.3 Erros em Python

#### ⚠️ **ERRO POTENCIAL 1: Falta de timeout**
- **Arquivo:** `actions/actions.py`, todas as requisições
- **Problema:** `requests.get/post` sem parâmetro `timeout`
- **Impacto:** Bot pode travar se API estiver lenta
- **Severidade:** MÉDIA

#### ⚠️ **ERRO POTENCIAL 2: Slot não limpo em caso de erro**
- **Arquivo:** `actions/actions.py`, `ActionBuscarAtendimentoDocente`
- **Problema:** Se houver exceção antes da linha 212, o slot não é limpo
- **Impacto:** Slot pode ficar "preso"
- **Severidade:** MÉDIA

#### ⚠️ **ERRO POTENCIAL 3: Comparação de string case-sensitive**
- **Arquivo:** `actions/actions.py`, linha 209
- **Problema:** `if nome_docente.lower() in doc.get('nome_professor', '').lower():`
- **Observação:** Na verdade está correto (usa `.lower()`), mas pode haver problemas com acentuação
- **Severidade:** BAIXA (mas pode melhorar com normalização Unicode)

### 3.4 Inconsistências entre Arquivos

#### ✅ **Todas as actions do domain.yml estão implementadas**
- Verificação realizada: 8 actions no domain.yml = 8 classes em actions.py ✅

#### ⚠️ **Intent `informar_disciplina` não tem regra**
- **Problema:** Intent existe no domain.yml mas não é usado em rules.yml
- **Impacto:** Se usuário digitar apenas "Cloud Computing", bot não saberá o que fazer
- **Severidade:** MÉDIA

---

## 4. 🚀 PRÓXIMOS PASSOS

### 4.1 Funcionalidades Prioritárias (Baseado no Estado Atual)

#### **1. Sistema de Validação de Entidades** 🔴 ALTA PRIORIDADE
**Por quê?**
- Atualmente, o bot aceita qualquer nome de disciplina/docente
- Se o usuário digitar "Engenharia de Software" mas a API esperar "Engenharia de Software" (com maiúsculas diferentes), pode falhar
- Melhora a experiência do usuário com feedback imediato

**Implementação:**
- Criar `ActionValidateFormAtendimentoDocente` que verifica se o nome do docente existe na API antes de buscar atendimento
- Criar `ActionValidateFormBuscarMaterial` que verifica se a disciplina existe
- Adicionar mensagens de erro amigáveis: "Não encontrei a disciplina X. Você quis dizer Y?"

**Impacto:** Reduz frustrações do usuário e melhora a precisão do bot.

---

#### **2. Sistema de Histórico e Contexto** 🟡 MÉDIA PRIORIDADE
**Por quê?**
- O bot não "lembra" de conversas anteriores na mesma sessão de forma inteligente
- Se o usuário perguntar "qual o horário?" depois de mencionar uma disciplina, o bot não sabe qual disciplina

**Implementação:**
- Usar slots para manter contexto (já parcialmente implementado)
- Adicionar stories que mostrem como o bot deve lidar com perguntas sem contexto explícito
- Exemplo: Se usuário perguntar "qual o horário?" sem mencionar disciplina, o bot deve perguntar "De qual disciplina?"

**Impacto:** Melhora significativamente a experiência conversacional.

---

#### **3. Sistema de Feedback e Aprendizado Contínuo** 🟢 BAIXA PRIORIDADE (mas importante para TCC)
**Por quê?**
- Para um TCC, é importante mostrar que o bot aprende e melhora
- Permite coletar dados sobre onde o bot falha

**Implementação:**
- Adicionar action `action_coletar_feedback` que pergunta ao usuário se a resposta foi útil
- Armazenar conversas problemáticas para análise posterior
- Criar endpoint na API FastAPI para receber feedback
- Dashboard simples mostrando taxa de sucesso

**Impacto:** Dados valiosos para o TCC e melhoria contínua do bot.

---

### 4.2 Melhorias Técnicas Recomendadas

1. **Adicionar logging estruturado** (para debug e análise)
2. **Implementar cache para requisições frequentes** (ex: lista de disciplinas)
3. **Adicionar testes automatizados** (usando `tests/test_stories.yml`)
4. **Documentar API endpoints** (para facilitar manutenção)

---

## 📋 RESUMO EXECUTIVO

### ✅ **Pontos Fortes do Projeto:**
- Arquitetura bem definida (Rasa + FastAPI)
- Código limpo e organizado
- Uso adequado de formulários e slots
- Boa cobertura de intents principais

### ⚠️ **Principais Problemas:**
1. **NLU:** Exemplos desequilibrados e algumas duplicatas
2. **Lógica:** Falta de timeout e tratamento de erros inconsistente
3. **Erros:** Typo na URL da API (crítico)
4. **Config:** Tokenizer não ideal para português

### 🎯 **Ações Imediatas Recomendadas:**
1. ✅ Corrigir typo na URL (linha 17 de actions.py)
2. ✅ Adicionar mais exemplos para intents sub-representados
3. ✅ Remover duplicatas do nlu.yml
4. ✅ Adicionar timeout em todas as requisições
5. ✅ Criar regra para intent `informar_disciplina`

---

**Análise realizada em:** {{ data_atual }}
**Versão do Rasa:** 3.1
**Status Geral:** 🟢 BOM (com melhorias recomendadas)

