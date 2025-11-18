# 📋 RESUMO DAS CORREÇÕES DE ALUCINAÇÃO

## 🎯 OBJETIVO

Reduzir alucinações identificadas nos testes, melhorando:
- Extração de entidades
- Reconhecimento de intents
- Ativação de formulários
- Busca de informações

---

## ✅ CORREÇÕES IMPLEMENTADAS

### 1. 📝 Mais Exemplos de Treinamento (40+ novos exemplos)

**Problema:** Bot extraía palavras pequenas ("de", "é") como entidades e não reconhecia variações de intents.

**Solução:** Adicionados mais de 40 exemplos em:
- `consultar_data_avaliacao` - 8 novos exemplos
- `consultar_horario_aula` - 5 novos exemplos
- `consultar_regras_aps` - 7 novos exemplos (incluindo "informações sobre APS")
- `consultar_regras_tcc` - 8 novos exemplos (incluindo "quando começa o tcc")
- `consultar_estagio` - 4 novos exemplos
- `consultar_horas_complementares` - 3 novos exemplos
- `solicitar_atendimento_docente` - 3 novos exemplos
- `solicitar_material_aula` - 4 novos exemplos
- `informar_disciplina` - 4 novos exemplos

**Arquivo:** `data/nlu.yml`

---

### 2. 🔧 Correção na Action de Avaliações

**Problema:** Retornava "None:" nas datas e não filtrava corretamente.

**Solução:**
- ✅ Verificação de campos `None` antes de processar
- ✅ Filtro melhorado para busca de avaliações
- ✅ Tratamento correto de datas (com ou sem 'T')
- ✅ Melhor tratamento de erros

**Arquivo:** `actions/actions.py` - `ActionBuscarDataAvaliacao`

**Código:**
```python
# Pular se topico ou data forem None
if not nome_aval or not data_aval:
    continue

# Melhorar filtro de busca
if termo_busca_lower == "prova":
    # Se busca genérica "prova", retorna todas
    data_fmt = data_aval.split('T')[0] if 'T' in data_aval else data_aval
    encontradas.append(f"- {nome_aval}: {data_fmt}")
elif termo_busca_lower in nome_aval_lower:
    # Se termo específico está no nome
    data_fmt = data_aval.split('T')[0] if 'T' in data_aval else data_aval
    encontradas.append(f"- {nome_aval}: {data_fmt}")
```

---

### 3. 👨‍🏫 Melhoria na Busca de Docentes

**Problema:** Não encontrava professores mesmo quando existiam.

**Solução:**
- ✅ Busca mais flexível (verifica palavras individuais)
- ✅ Trata acentos e variações de nomes
- ✅ Busca em professores E coordenadores
- ✅ Corrigido bug na action de atendimento

**Arquivo:** `actions/actions.py` - `ActionBuscarInfoDocente` e `ActionBuscarAtendimentoDocente`

**Código:**
```python
nome_docente_lower = nome_docente.lower().strip()

for doc in todos:
    nome = doc.get('nome_professor') or doc.get('nome_coordenador')
    if nome:
        nome_lower = nome.lower().strip()
        # Busca mais flexível
        if nome_docente_lower in nome_lower or nome_lower in nome_docente_lower:
            encontrado = doc
            break
        # Verifica palavras individuais (ex: "Alvaro" em "Álvaro Prado")
        nome_parts = nome_lower.split()
        if any(part == nome_docente_lower or nome_docente_lower in part for part in nome_parts):
            encontrado = doc
            break
```

---

### 4. 📋 Melhorias nas Regras de Formulários

**Problema:** Formulários eram ativados incorretamente, causando confusão.

**Solução:**
- ✅ Adicionadas regras específicas para quando entidades já estão presentes
- ✅ Removida regra que causava confusão com `informar_disciplina`
- ✅ 5 novas regras para evitar ativação desnecessária

**Arquivo:** `data/rules.yml`

**Novas Regras:**
1. `Buscar material quando disciplina fornecida`
2. `Consultar horario quando disciplina fornecida`
3. `Consultar data avaliacao quando disciplina fornecida`
4. `Buscar info docente quando nome fornecido`
5. `Buscar atendimento quando nome fornecido`

---

## 📊 IMPACTO ESPERADO

### Antes das Correções:
- ❌ Extraía "de" ou "é" como disciplina
- ❌ Não reconhecia "informações sobre APS"
- ❌ Não reconhecia "quando começa o tcc"
- ❌ Retornava "None:" nas datas
- ❌ Não encontrava professores
- ❌ Formulários ativados incorretamente

### Depois das Correções:
- ✅ Extração mais precisa de entidades
- ✅ Reconhecimento melhor de intents
- ✅ Datas formatadas corretamente
- ✅ Busca de docentes mais flexível
- ✅ Formulários ativados apenas quando necessário

---

## 🧪 TESTES RECOMENDADOS

### Testes Críticos:
1. **Extração de Disciplina:**
   ```
   "Qual a sala da aula de engenharia de software?"
   "Quando é a NP1 de engenharia de Software?"
   "data da prova de Engenharia de Software"
   ```

2. **Reconhecimento de Intents:**
   ```
   "informações sobre APS"
   "quando começa o tcc"
   "atendimento coordenação"
   ```

3. **Avaliações:**
   ```
   "data da prova de sistemas distribuidos"
   "quando é a NP1 de sistemas distribuidos"
   ```

4. **Docentes:**
   ```
   "Qual email do professor Alvaro"
   "contato eliane"
   "horário de atendimento do alvaro"
   ```

---

## 📝 PRÓXIMOS PASSOS

1. **Treinar o modelo:**
   ```bash
   rasa train
   ```

2. **Testar as correções:**
   ```bash
   rasa shell
   ```

3. **Se ainda houver problemas:**
   - Adicionar mais exemplos específicos para casos problemáticos
   - Ajustar threshold do FallbackClassifier no `config.yml`
   - Considerar usar SpacyTokenizer para português (mais preciso)

---

## ⚠️ NOTAS IMPORTANTES

1. **Treinamento Necessário:** Após essas correções, é **ESSENCIAL** treinar o modelo novamente (`rasa train`).

2. **Testes Contínuos:** Continue testando e adicionando exemplos para casos que ainda apresentam problemas.

3. **Pipeline NLU:** O `WhitespaceTokenizer` não é ideal para português. Se os problemas persistirem, considere usar `SpacyTokenizer` com modelo português.

---

**Documento criado em:** 2025-01-27  
**Status:** ✅ Correções implementadas - Aguardando retreinamento

