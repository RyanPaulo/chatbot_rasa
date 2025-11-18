# 🚨 RESUMO DOS PROBLEMAS CRÍTICOS DE INTEGRAÇÃO RASA ↔ API

## ⚠️ PROBLEMAS CRÍTICOS IDENTIFICADOS

Após análise completa da API FastAPI, identifiquei **2 problemas críticos** que impedem o funcionamento correto do chatbot:

---

## 🔴 PROBLEMA 1: Endpoint de Busca de Disciplina por Nome NÃO EXISTE

### Situação Atual:
- **Rasa usa:** `/disciplinas/get_disciplina_id/{disciplina_nome}`
- **API tem:** `/disciplinas/get_diciplina_id/{disciplina_id}` que espera **UUID**, não nome!

### Impacto:
- ❌ `ActionBuscarCronograma` - **NÃO FUNCIONA**
- ❌ `ActionBuscarDataAvaliacao` - **NÃO FUNCIONA**  
- ❌ `ActionBuscarMaterial` - **NÃO FUNCIONA** (além do problema 2)

### Solução Temporária:
Usar o endpoint `/disciplinas/get_diciplina_nome/{nome}/cronograma` que internamente busca o ID, mas é ineficiente.

### Solução Ideal:
Criar endpoint na API: `GET /disciplinas/get_id_por_nome/{nome_disciplina}`

---

## 🔴 PROBLEMA 2: Endpoint de Busca de Documentos NÃO EXISTE

### Situação Atual:
- **Rasa usa:** `/documento/disciplina/{id_disciplina}`
- **API tem:** Apenas `POST /documentos/upload` - **NÃO HÁ ENDPOINT GET!**

### Impacto:
- ❌ `ActionBuscarMaterial` - **SEMPRE RETORNA 404**

### Solução Temporária:
Usar `/baseconhecimento/get_buscar?q={nome_disciplina}` mas não retorna URLs dos documentos diretamente.

### Solução Ideal:
Criar endpoint na API: `GET /baseconhecimento/disciplina/{disciplina_id}` que retorna documentos com URLs.

---

## 🟡 PROBLEMA 3: Formato de Resposta Diferente

### Situação:
- **Rasa espera:** Lista direta `[{...}]`
- **API retorna:** `{"contextos": [...]}`

### Impacto:
- ⚠️ `ActionBuscarInfoAtividadeAcademica` - Lê formato errado

### Solução:
Corrigir código do Rasa para ler `dados.get("contextos", [])`

---

## 📊 STATUS DOS ENDPOINTS

| Funcionalidade | Endpoint Rasa | Endpoint API | Status |
|----------------|---------------|-------------|--------|
| Buscar ID Disciplina | `/disciplinas/get_disciplina_id/{nome}` | `/disciplinas/get_diciplina_id/{uuid}` | ❌ **ERRADO** |
| Buscar Documentos | `/documento/disciplina/{id}` | **NÃO EXISTE** | ❌ **CRÍTICO** |
| Buscar Cronograma | `/cronograma/disciplina/{id}` | `/cronograma/disciplina/{id}` | ✅ OK (mas precisa ID) |
| Buscar Avaliação | `/avaliacao/disciplina/{id}` | `/avaliacao/disciplina/{id}` | ✅ OK (mas precisa ID) |
| Buscar Base Conhecimento | `/baseconhecimento/get_buscar?q={}` | `/baseconhecimento/get_buscar?q={}` | ⚠️ Formato diferente |
| Gerar Resposta IA | `/ia/gerar-resposta` | `/ia/gerar-resposta` | ✅ **PERFEITO** |
| Buscar Avisos | `/aviso/get_lista_aviso/` | `/aviso/get_lista_aviso/` | ✅ **PERFEITO** |
| Buscar Professores | `/professores/lista_professores/` | `/professores/lista_professores/` | ✅ **PERFEITO** |

---

## 🔧 CORREÇÕES URGENTES NO RASA

### 1. Corrigir `get_disciplina_id_by_name`
```python
def get_disciplina_id_by_name(disciplina_nome: Text) -> str | None:
    try:
        # Usar endpoint de cronograma que busca por nome
        response = requests.get(
            f"{API_URL}/disciplinas/get_diciplina_nome/{disciplina_nome}/cronograma",
            timeout=10
        )
        if response.ok:
            cronogramas = response.json()
            if cronogramas and len(cronogramas) > 0:
                return cronogramas[0].get('id_disciplina')
        return None
    except:
        return None
```

### 2. Corrigir `ActionBuscarMaterial`
```python
# Usar busca na base de conhecimento como alternativa
response = requests.get(
    f"{API_URL}/baseconhecimento/get_buscar", 
    params={"q": disciplina_nome}, 
    timeout=10
)
```

### 3. Corrigir `ActionBuscarInfoAtividadeAcademica`
```python
dados = response.json()
contextos = dados.get("contextos", [])  # Ler formato correto
```

---

## 📝 RECOMENDAÇÕES PARA A API (Documentar)

### Endpoints que Seriam Úteis:

1. **`GET /disciplinas/get_id_por_nome/{nome_disciplina}`**
   - Retorna: `{"id_disciplina": "uuid", "nome_disciplina": "..."}`
   - Usa busca `.ilike()` para flexibilidade

2. **`GET /baseconhecimento/disciplina/{disciplina_id}`**
   - Retorna: `[{"nome_arquivo_origem": "...", "url_documento": "...", ...}]`
   - Lista documentos de uma disciplina

3. **`GET /baseconhecimento/disciplina_nome/{nome_disciplina}`**
   - Versão que busca por nome da disciplina
   - Retorna documentos com URLs

---

## ✅ PRÓXIMOS PASSOS

### Imediato (No Rasa):
1. ✅ Corrigir `get_disciplina_id_by_name` (usar endpoint de cronograma)
2. ✅ Corrigir `ActionBuscarMaterial` (usar busca alternativa)
3. ✅ Corrigir `ActionBuscarInfoAtividadeAcademica` (ler formato correto)

### Futuro (Na API - Documentar):
1. Criar endpoint de busca de ID por nome
2. Criar endpoint de busca de documentos por disciplina
3. Documentar formatos de resposta

---

**Documento criado em:** 2025-01-27
**Baseado em:** Análise real da API FastAPI

