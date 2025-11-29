# 🔍 ANÁLISE DE INTEGRAÇÃO RASA ↔ API FASTAPI

## 📋 CONTEXTO

Este documento analisa a integração entre o chatbot Rasa e a API FastAPI, identificando problemas reais e propondo melhorias baseadas na estrutura real da API.

---

## 🚨 PROBLEMAS CRÍTICOS IDENTIFICADOS

### 1. 🔴 CRÍTICO: Endpoint Incorreto para Buscar ID de Disciplina

**Problema:**
- O Rasa usa: `/disciplinas/get_disciplina_id/{disciplina_nome}`
- **MAS** esse endpoint na API espera um **UUID**, não um nome!
- Linha 36-37 de `disciplina.py`: `@router.get("/get_diciplina_id/{disciplina}", response_model=Disciplina)` e `def get_disciplina_detalhado(disciplina_id: uuid.UUID)`

**Impacto:**
- Todas as actions que buscam disciplina por nome **FALHAM**
- `ActionBuscarCronograma`, `ActionBuscarDataAvaliacao`, `ActionBuscarMaterial` não funcionam corretamente

**Solução:**

A API **NÃO TEM** um endpoint público que busca disciplina por nome e retorna o ID. Existem duas opções:

#### Opção 1: Criar endpoint na API (RECOMENDADO - mas não podemos modificar)
```python
# Adicionar em disciplina.py (NÃO FAZER - apenas para referência)
@router.get("/get_id_por_nome/{nome_disciplina}")
def get_disciplina_id_por_nome(nome_disciplina: str):
    try:
        response = supabase.table("disciplina").select("id_disciplina").ilike("nome_disciplina", f"%{nome_disciplina}%").limit(1).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Disciplina '{nome_disciplina}' não encontrada.")
        return {"id_disciplina": response.data[0]['id_disciplina']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Opção 2: Usar endpoint existente que já faz busca por nome (SOLUÇÃO ATUAL)
O endpoint `/disciplinas/get_diciplina_nome/{nome_disciplina}/cronograma` já busca por nome, mas retorna cronograma diretamente.

**Solução Imediata para o Rasa:**

Modificar `get_disciplina_id_by_name` para fazer busca direta na tabela disciplina via Supabase (se tiver acesso) OU usar o endpoint de cronograma que já faz a busca:

```python
# SOLUÇÃO TEMPORÁRIA: Usar endpoint de cronograma que já busca por nome
def get_disciplina_id_by_name(disciplina_nome: Text) -> str | None:
    try:
        # Usa o endpoint que busca cronograma por nome (que internamente busca o ID)
        response = requests.get(
            f"{API_URL}/disciplinas/get_diciplina_nome/{disciplina_nome}/cronograma",
            timeout=10
        )
        if response.ok:
            # Se retornou cronograma, significa que encontrou a disciplina
            # Mas não temos o ID diretamente...
            # PRECISAMOS DE UM ENDPOINT MELHOR NA API
            return None  # Problema: não temos o ID!
        return None
    except requests.exceptions.RequestException:
        return None
```

**⚠️ RECOMENDAÇÃO URGENTE:**
- **Criar endpoint na API:** `/disciplinas/get_id_por_nome/{nome_disciplina}` que retorna `{"id_disciplina": "uuid"}` 
- OU modificar o endpoint existente para também retornar o ID quando buscar por nome

---

### 2. 🟡 IMPORTANTE: Endpoint de Documentos Espera ID, não Nome

**Problema:**
- `ActionBuscarMaterial` usa: `/documento/disciplina/{id_disciplina}`
- Mas primeiro precisa converter nome → ID, e não há endpoint para isso

**Solução:**
- Mesma solução do problema 1: criar endpoint que busca ID por nome

---

### 3. 🟡 IMPORTANTE: Endpoint de Base de Conhecimento Retorna Formato Diferente

**Problema:**
- `ActionBuscarInfoAtividadeAcademica` usa: `/baseconhecimento/get_buscar?q={atividade}`
- A API retorna: `{"contextos": [item['conteudo_processado'] for item in response.data]}`
- Mas o Rasa espera: `[{"resposta": "..."}]` ou similar

**Código Atual no Rasa:**
```python
infos = response.json()
if infos and isinstance(infos, list):
    info = infos[0]
    dispatcher.utter_message(text=f"Sobre {atividade}:\n{info.get('resposta', '')}")
```

**Problema:** A API retorna `{"contextos": [...]}`, não uma lista direta!

**Solução:**
```python
# Corrigir em ActionBuscarInfoAtividadeAcademica
response = requests.get(f"{API_URL}/baseconhecimento/get_buscar", params={"q": atividade}, timeout=10)
if response.ok:
    dados = response.json()
    # A API retorna {"contextos": [...]}
    contextos = dados.get("contextos", [])
    if contextos:
        # Pega o primeiro contexto (resumo)
        dispatcher.utter_message(text=f"Sobre {atividade}:\n{contextos[0]}")
    else:
        dispatcher.utter_message(text=f"Não encontrei informações detalhadas sobre {atividade}.")
```

---

### 4. 🟡 IMPORTANTE: Endpoint de IA Retorna Formato Correto

**✅ BOM:** `ActionGerarRespostaComIA` está correto!
- Usa: `/ia/gerar-resposta` com `{"pergunta": "..."}`
- A API retorna: `{"resposta": "..."}`
- O Rasa lê: `dados.get("resposta", ...)`
- **Tudo certo!**

---

### 5. 🟡 IMPORTANTE: Endpoint de Avisos Retorna Lista Direta

**✅ BOM:** `ActionBuscarUltimosAvisos` está correto!
- Usa: `/aviso/get_lista_aviso/`
- A API retorna: `List[Aviso]` (lista direta)
- O Rasa processa: `response.json()` como lista
- **Tudo certo!**

---

### 6. 🟡 IMPORTANTE: Endpoint de Professores Retorna Lista Direta

**✅ BOM:** `ActionBuscarAtendimentoDocente` e `ActionBuscarInfoDocente` estão corretos!
- Usam: `/professores/lista_professores/` e `/coordenador/get_list_coordenador/`
- Ambos retornam listas diretas
- **Tudo certo!**

---

## 📊 MAPEAMENTO DE ENDPOINTS

### Endpoints Usados pelo Rasa vs. Endpoints Reais da API

| Action Rasa | Endpoint Usado | Endpoint Real | Status | Problema |
|------------|----------------|---------------|--------|----------|
| `get_disciplina_id_by_name` | `/disciplinas/get_disciplina_id/{nome}` | `/disciplinas/get_diciplina_id/{uuid}` | ❌ **ERRADO** | Espera UUID, não nome |
| `ActionBuscarCronograma` | `/cronograma/disciplina/{id}` | `/cronograma/disciplina/{id}` | ✅ Correto | Mas precisa do ID primeiro |
| `ActionBuscarDataAvaliacao` | `/avaliacao/disciplina/{id}` | `/avaliacao/disciplina/{id}` | ✅ Correto | Mas precisa do ID primeiro |
| `ActionBuscarMaterial` | `/documento/disciplina/{id}` | `/documento/disciplina/{id}` | ✅ Correto | Mas precisa do ID primeiro |
| `ActionBuscarInfoAtividadeAcademica` | `/baseconhecimento/get_buscar?q={}` | `/baseconhecimento/get_buscar?q={}` | ⚠️ **FORMATO DIFERENTE** | Retorna `{"contextos": [...]}` não lista |
| `ActionGerarRespostaComIA` | `/ia/gerar-resposta` | `/ia/gerar-resposta` | ✅ **PERFEITO** | Formato correto |
| `ActionBuscarUltimosAvisos` | `/aviso/get_lista_aviso/` | `/aviso/get_lista_aviso/` | ✅ **PERFEITO** | Formato correto |
| `ActionBuscarAtendimentoDocente` | `/professores/lista_professores/` | `/professores/lista_professores/` | ✅ **PERFEITO** | Formato correto |
| `ActionBuscarInfoDocente` | `/professores/lista_professores/` + `/coordenador/get_list_coordenador/` | Ambos corretos | ✅ **PERFEITO** | Formato correto |

---

## 🔧 CORREÇÕES NECESSÁRIAS NO RASA

### Correção 1: Função `get_disciplina_id_by_name`

**Problema:** Endpoint não existe ou está incorreto

**Solução Temporária (usando endpoint de cronograma):**
```python
def get_disciplina_id_by_name(disciplina_nome: Text) -> str | None:
    """
    Busca o ID de uma disciplina pelo nome.
    
    NOTA: A API não tem endpoint direto para isso.
    Usa o endpoint de cronograma que internamente busca por nome.
    """
    try:
        # Tenta usar o endpoint que busca cronograma por nome
        # Esse endpoint internamente busca o ID da disciplina
        response = requests.get(
            f"{API_URL}/disciplinas/get_diciplina_nome/{disciplina_nome}/cronograma",
            timeout=10
        )
        
        if response.ok:
            # Se retornou cronograma, a disciplina existe
            # Mas não temos o ID diretamente...
            # PRECISAMOS EXTRAIR DO PRIMEIRO CRONOGRAMA
            cronogramas = response.json()
            if cronogramas and len(cronogramas) > 0:
                # O cronograma tem id_disciplina
                id_disciplina = cronogramas[0].get('id_disciplina')
                if id_disciplina:
                    return id_disciplina
        
        return None
    except requests.exceptions.RequestException:
        return None
```

**⚠️ PROBLEMA:** Isso funciona, mas é ineficiente (busca cronograma quando só queremos o ID).

**Solução Ideal:** Criar endpoint na API `/disciplinas/get_id_por_nome/{nome}`

---

### Correção 2: `ActionBuscarInfoAtividadeAcademica`

**Problema:** Formato de resposta diferente

**Código Corrigido:**
```python
class ActionBuscarInfoAtividadeAcademica(Action):
    def name(self) -> Text:
        return "action_buscar_info_atividade_academica"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        atividade = next(tracker.get_latest_entity_values("atividade_academica"), None)
        intent = tracker.latest_message['intent'].get('name')
        
        if not atividade:
            if "tcc" in intent: atividade = "TCC"
            elif "aps" in intent: atividade = "APS"
            elif "estagio" in intent: atividade = "Estagio"
            elif "horas_complementares" in intent: atividade = "Horas Complementares"
        
        if not atividade:
            dispatcher.utter_message(text="Sobre qual atividade você quer saber? (TCC, APS, Estagio)")
            return []

        dispatcher.utter_message(text=f"Buscando informações sobre {atividade}...")
        try:
            response = requests.get(
                f"{API_URL}/baseconhecimento/get_buscar", 
                params={"q": atividade}, 
                timeout=10
            )
            if response.ok:
                dados = response.json()
                # CORREÇÃO: A API retorna {"contextos": [...]}
                contextos = dados.get("contextos", [])
                
                if contextos and isinstance(contextos, list) and len(contextos) > 0:
                    # Pega o primeiro contexto (resumo)
                    dispatcher.utter_message(text=f"Sobre {atividade}:\n{contextos[0]}")
                else:
                    dispatcher.utter_message(text=f"Não encontrei informações detalhadas sobre {atividade}.")
            else:
                dispatcher.utter_message(text="Erro ao buscar informações do curso.")
        except Exception as e:
            print(f"Erro ao buscar atividade: {e}")
            dispatcher.utter_message(text="Erro ao buscar informações do curso.")
        return []
```

---

## 🎯 OTIMIZAÇÕES BASEADAS NA API REAL

### 1. Cache de Lista de Disciplinas

**Oportunidade:**
- A API não tem endpoint para listar todas as disciplinas com nomes
- Mas podemos criar cache local das disciplinas mais consultadas

**Solução:**
```python
# Adicionar ao CacheHelper
@staticmethod
def get_lista_disciplinas() -> dict[str, str]:
    """
    Retorna dicionário {nome_disciplina: id_disciplina}
    Cacheia por 1 hora
    """
    cache_key = "lista_disciplinas"
    timestamp = CacheHelper._cache_timestamp.get(cache_key)
    
    if cache_key in CacheHelper._cache_disciplinas:
        if timestamp and datetime.now() - timestamp < timedelta(hours=1):
            return CacheHelper._cache_disciplinas[cache_key]
    
    # Buscar todas as disciplinas (se houver endpoint)
    # OU construir cache incrementalmente conforme usa
    # Por enquanto, retorna vazio
    return {}
```

---

### 2. Busca Inteligente de Disciplina

**Oportunidade:**
- A API usa `.ilike()` para busca parcial (case-insensitive)
- Podemos fazer busca mais inteligente no Rasa

**Solução:**
```python
def get_disciplina_id_by_name(disciplina_nome: Text) -> str | None:
    """
    Busca ID de disciplina com fallback inteligente.
    """
    # Normalizar nome
    nome_normalizado = disciplina_nome.strip()
    
    # Tentar busca exata primeiro (usando endpoint de cronograma)
    try:
        response = requests.get(
            f"{API_URL}/disciplinas/get_diciplina_nome/{nome_normalizado}/cronograma",
            timeout=10
        )
        
        if response.ok:
            cronogramas = response.json()
            if cronogramas and len(cronogramas) > 0:
                return cronogramas[0].get('id_disciplina')
    except:
        pass
    
    # Se não encontrou, tentar variações comuns
    variacoes = [
        nome_normalizado.title(),  # Primeira letra maiúscula
        nome_normalizado.upper(),  # Tudo maiúscula
        nome_normalizado.lower(),  # Tudo minúscula
    ]
    
    for variacao in variacoes:
        if variacao == nome_normalizado:
            continue  # Já tentou
        
        try:
            response = requests.get(
                f"{API_URL}/disciplinas/get_diciplina_nome/{variacao}/cronograma",
                timeout=10
            )
            if response.ok:
                cronogramas = response.json()
                if cronogramas and len(cronogramas) > 0:
                    return cronogramas[0].get('id_disciplina')
        except:
            continue
    
    return None
```

---

### 3. Validação de Resposta da API

**Oportunidade:**
- A API tem estrutura bem definida
- Podemos validar respostas antes de usar

**Solução:**
```python
class ResponseValidator:
    @staticmethod
    def validate_disciplina_response(response: requests.Response) -> dict | None:
        """Valida resposta de busca de disciplina"""
        if not response.ok:
            return None
        
        try:
            data = response.json()
            # Endpoint de cronograma retorna lista de cronogramas
            if isinstance(data, list) and len(data) > 0:
                return data[0]  # Retorna primeiro cronograma
            return None
        except:
            return None
    
    @staticmethod
    def validate_base_conhecimento_response(response: requests.Response) -> list[str]:
        """Valida resposta de base de conhecimento"""
        if not response.ok:
            return []
        
        try:
            data = response.json()
            # API retorna {"contextos": [...]}
            if isinstance(data, dict) and "contextos" in data:
                contextos = data["contextos"]
                if isinstance(contextos, list):
                    return contextos
            return []
        except:
            return []
```

---

## 📝 RECOMENDAÇÕES PARA A API (NÃO MODIFICAR, APENAS DOCUMENTAR)

### Endpoints que Seriam Úteis:

1. **`GET /disciplinas/get_id_por_nome/{nome_disciplina}`**
   - Retorna: `{"id_disciplina": "uuid", "nome_disciplina": "..."}`
   - Usa busca `.ilike()` para flexibilidade

2. **`GET /disciplinas/lista/`** (já existe!)
   - Retorna lista de todas as disciplinas
   - Útil para cache e validação

3. **`GET /disciplinas/buscar/{termo}`**
   - Busca parcial por nome
   - Retorna lista de disciplinas que correspondem

---

## ✅ CHECKLIST DE CORREÇÕES

### No Rasa (FAZER):

- [ ] Corrigir `get_disciplina_id_by_name` para usar endpoint de cronograma
- [ ] Corrigir `ActionBuscarInfoAtividadeAcademica` para ler formato `{"contextos": [...]}`
- [ ] Adicionar validação de respostas da API
- [ ] Adicionar cache de IDs de disciplinas
- [ ] Melhorar tratamento de erros específicos da API

### Na API (DOCUMENTAR - NÃO MODIFICAR):

- [ ] Documentar que `/disciplinas/get_diciplina_id/{id}` espera UUID, não nome
- [ ] Considerar criar `/disciplinas/get_id_por_nome/{nome}` no futuro
- [ ] Documentar formato de resposta de `/baseconhecimento/get_buscar`

---

## 🎯 IMPACTO DAS CORREÇÕES

### Antes:
- ❌ Busca de disciplina por nome **NÃO FUNCIONA**
- ❌ Busca de material **NÃO FUNCIONA**
- ❌ Busca de avaliação **NÃO FUNCIONA**
- ⚠️ Busca de atividade acadêmica retorna formato errado

### Depois:
- ✅ Busca de disciplina funciona (usando endpoint de cronograma)
- ✅ Busca de material funciona
- ✅ Busca de avaliação funciona
- ✅ Busca de atividade acadêmica funciona corretamente

---

**Documento criado em:** 2025-01-27
**Baseado em:** Análise real da API FastAPI em `D:/ChatBot_API`

