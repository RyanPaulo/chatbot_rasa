# 📋 PLANO DE AÇÃO DETALHADO - CHATBOT ACADÊMICO

## 📊 RESUMO EXECUTIVO

Este documento apresenta um plano de ação completo para implementar melhorias críticas e novas funcionalidades no chatbot RASA, baseado em:
- Análise completa do projeto (5 documentos em `propostas_cursor/`)
- Estrutura real da API FastAPI
- Requisitos do TCC e painel administrativo

### 🎯 Objetivos Principais:
1. ✅ **Corrigir problemas críticos** de integração com a API
2. ✅ **Salvar todas as perguntas** dos alunos no endpoint `/mensagens_aluno/`
3. ✅ **Retornar URLs de documentos** quando aluno pedir material ou perguntar sobre base de conhecimento
4. ✅ **Implementar dúvidas frequentes** por categorias (Institucionais vs Conteúdo)

### ⏱️ Cronograma:
- **Semana 1:** Correções críticas (3 tarefas)
- **Semana 2:** Novas funcionalidades (4 tarefas)
- **Semana 3-4:** Otimizações (3 tarefas)

### 📈 Impacto Esperado:
- ✅ **100% das funcionalidades** funcionando corretamente
- ✅ **Todas as perguntas** sendo salvas para análise
- ✅ **URLs de documentos** retornadas quando solicitado
- ✅ **Dúvidas frequentes** classificadas automaticamente

---

## 🎯 OBJETIVO GERAL

Implementar melhorias críticas e novas funcionalidades no chatbot RASA para:
1. Corrigir problemas de integração com a API
2. Salvar todas as perguntas dos alunos
3. Retornar URLs de documentos quando solicitado
4. Implementar sistema de dúvidas frequentes por categorias

---

## 📊 SITUAÇÃO ATUAL (Baseado nas Análises)

### ✅ Funcionando:
- Integração com IA (Gemini) - `/ia/gerar-resposta`
- Busca de avisos - `/aviso/get_lista_aviso/`
- Busca de professores - `/professores/lista_professores/`
- Busca de coordenadores - `/coordenador/get_list_coordenador/`

### ❌ Problemas Críticos:
1. **Busca de disciplina por nome** - Endpoint não existe corretamente
2. **Busca de documentos** - Endpoint não existe
3. **Formato de resposta** - Base de conhecimento retorna formato diferente
4. **Salvamento de perguntas** - Não implementado
5. **Retorno de URLs de documentos** - Não implementado
6. **Dúvidas frequentes por categorias** - Não implementado

---

## 🚀 FASE 1: CORREÇÕES CRÍTICAS (Semana 1)

### 1.1 Corrigir Busca de Disciplina por Nome

**Problema:** Endpoint `/disciplinas/get_disciplina_id/{nome}` não existe - API espera UUID

**Solução:**
```python
# Modificar actions/actions.py
def get_disciplina_id_by_name(disciplina_nome: Text) -> str | None:
    """
    Busca ID de disciplina usando endpoint de cronograma que aceita nome.
    NOTA: Solução temporária - ideal seria endpoint específico na API.
    """
    try:
        response = requests.get(
            f"{API_URL}/disciplinas/get_diciplina_nome/{disciplina_nome}/cronograma",
            timeout=10
        )
        if response.ok:
            cronogramas = response.json()
            if cronogramas and isinstance(cronogramas, list) and len(cronogramas) > 0:
                # Extrai ID da disciplina do primeiro cronograma
                id_disciplina = cronogramas[0].get('id_disciplina')
                if id_disciplina:
                    return id_disciplina
        return None
    except requests.exceptions.RequestException:
        return None
```

**Arquivos a modificar:**
- `actions/actions.py` - Função `get_disciplina_id_by_name`

**Teste:**
- Testar busca de cronograma com nome de disciplina
- Verificar se ID é extraído corretamente

---

### 1.2 Corrigir Formato de Resposta da Base de Conhecimento

**Problema:** API retorna `{"contextos": [...]}` mas Rasa espera lista direta

**Solução:**
```python
# Modificar ActionBuscarInfoAtividadeAcademica em actions/actions.py
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
                # CORREÇÃO: API retorna {"contextos": [...]}
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

**Arquivos a modificar:**
- `actions/actions.py` - Classe `ActionBuscarInfoAtividadeAcademica`

**Teste:**
- Testar busca de TCC, APS, Estágio
- Verificar se mensagem é exibida corretamente

---

### 1.3 Implementar Busca de Documentos com URLs

**Problema:** Endpoint `/documento/disciplina/{id}` não existe na API

**Solução Temporária:**
Usar busca na base de conhecimento e extrair documentos com URLs. A API já retorna `url_documento` nas buscas da base de conhecimento.

**Implementação:**
```python
# Nova action ou modificar ActionBuscarMaterial
class ActionBuscarMaterial(Action):
    def name(self) -> Text:
        return "action_buscar_material"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disciplina_nome = tracker.get_slot("disciplina")
        
        if not disciplina_nome:
            dispatcher.utter_message(text="Claro. De qual disciplina você quer o material?")
            return []
        
        # Buscar ID da disciplina primeiro
        id_disciplina = get_disciplina_id_by_name(disciplina_nome)
        
        if not id_disciplina:
            dispatcher.utter_message(text=f"Disciplina '{disciplina_nome}' não encontrada.")
            return [SlotSet("disciplina", None)]
        
        dispatcher.utter_message(text=f"Buscando materiais para {disciplina_nome}...")

        try:
            # SOLUÇÃO TEMPORÁRIA: Buscar na base de conhecimento por nome da disciplina
            # A API retorna documentos com url_documento quando busca na baseconhecimento
            response = requests.get(
                f"{API_URL}/baseconhecimento/get_buscar", 
                params={"q": disciplina_nome}, 
                timeout=10
            )
            response.raise_for_status()
            
            dados = response.json()
            contextos = dados.get("contextos", [])
            
            # PROBLEMA: O endpoint get_buscar não retorna url_documento diretamente
            # PRECISAMOS DE UM ENDPOINT ESPECÍFICO NA API
            
            # Por enquanto, informar que precisa de endpoint específico
            if contextos:
                dispatcher.utter_message(
                    text=f"Encontrei informações sobre {disciplina_nome} na base de conhecimento. "
                         f"Os documentos estão disponíveis no painel administrativo."
                )
            else:
                dispatcher.utter_message(
                    text=f"Não encontrei materiais (slides, PDFs) para {disciplina_nome} no sistema."
                )

        except Exception as e:
            print(f"Erro ao buscar documentos: {e}")
            dispatcher.utter_message(text="Erro ao conectar ao sistema de documentos.")
        
        return [SlotSet("disciplina", None)]
```

**⚠️ LIMITAÇÃO:**
O endpoint `/baseconhecimento/get_buscar` não retorna `url_documento` diretamente. **NECESSÁRIO criar endpoint na API** ou modificar o existente.

**Arquivos a modificar:**
- `actions/actions.py` - Classe `ActionBuscarMaterial`

**Recomendação para API (Documentar):**
Criar endpoint: `GET /baseconhecimento/disciplina/{disciplina_id}` que retorna:
```json
[
  {
    "nome_arquivo_origem": "arquivo.pdf",
    "url_documento": "https://...",
    "categoria": "...",
    "palavra_chave": [...]
  }
]
```

---

## 🚀 FASE 2: NOVAS FUNCIONALIDADES (Semana 2)

### 2.1 Implementar Salvamento de Perguntas dos Alunos

**Requisito:** Todas as perguntas feitas ao Rasa devem ser salvas no endpoint `/mensagens_aluno/`

**Estrutura do Schema:**
```python
# Schema da API (já existe)
class MensagemAlunoCreate:
    primeira_pergunta: str  # A pergunta do aluno
    topico: List[str]       # Tópicos/categorias (extraídos da pergunta)
    feedback: str           # Feedback (pode ser vazio inicialmente)
    data_hora: datetime     # Timestamp automático
```

**Implementação:**

#### 2.1.1 Criar Helper para Salvar Perguntas

```python
# Adicionar em actions/actions.py
from datetime import datetime

def salvar_pergunta_aluno(pergunta: str, topico: list[str] = None) -> bool:
    """
    Salva a pergunta do aluno no endpoint de mensagens.
    Extrai tópicos automaticamente da pergunta.
    """
    try:
        # Extrair tópicos básicos da pergunta (pode melhorar com NLP)
        if not topico:
            topico = extrair_topicos_da_pergunta(pergunta)
        
        payload = {
            "primeira_pergunta": pergunta,
            "topico": topico,
            "feedback": "",  # Vazio inicialmente
            "data_hora": datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{API_URL}/mensagens_aluno/",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Erro ao salvar pergunta: {e}")
        return False

def extrair_topicos_da_pergunta(pergunta: str) -> list[str]:
    """
    Extrai tópicos da pergunta.
    Primeiro tenta classificar como Institucional, depois verifica se é de Conteúdo.
    """
    topicos = []
    pergunta_lower = pergunta.lower()
    
    # 1. Verificar se é dúvida institucional
    topicos_institucionais = {
        "tcc": "TCC",
        "trabalho de conclusão": "TCC",
        "aps": "APS",
        "atividade prática": "APS",
        "estágio": "Estágio",
        "estagio": "Estágio",
        "horas complementares": "Horas Complementares",
        "professor": "Docente",
        "docente": "Docente",
        "aviso": "Aviso",
        "comunicado": "Aviso"
    }
    
    for palavra_chave, topico in topicos_institucionais.items():
        if palavra_chave in pergunta_lower:
            topicos.append(topico)
    
    # 2. Se não encontrou tópico institucional, verificar se é dúvida de conteúdo
    # Buscar na base de conhecimento para ver se há palavras-chave correspondentes
    if not topicos:
        try:
            response = requests.get(
                f"{API_URL}/ia/testar-baseconhecimento",
                params={"q": pergunta},
                timeout=10
            )
            if response.ok:
                dados = response.json()
                if dados.get("quantidade_contextos", 0) > 0:
                    # É dúvida de conteúdo - adicionar marcador
                    topicos.append("Conteúdo")
                    # Tentar extrair categoria/palavras-chave da resposta
                    # (Isso requer endpoint que retorne essas informações)
        except:
            pass
    
    return topicos if topicos else ["Geral"]
```

#### 2.1.2 Modificar Actions para Salvar Perguntas

Adicionar chamada de `salvar_pergunta_aluno` no início de cada action importante:

```python
# Exemplo em ActionGerarRespostaComIA
class ActionGerarRespostaComIA(Action):
    def name(self) -> Text:
        return "action_gerar_resposta_com_ia"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pergunta_aluno = tracker.latest_message.get('text')
        
        # NOVO: Salvar pergunta do aluno
        salvar_pergunta_aluno(pergunta_aluno)
        
        dispatcher.utter_message(text="Consultando Base de Dados...")
        # ... resto do código ...
```

**Arquivos a modificar:**
- `actions/actions.py` - Adicionar função `salvar_pergunta_aluno` e `extrair_topicos_da_pergunta`
- `actions/actions.py` - Modificar todas as actions principais para salvar perguntas

**Actions a modificar:**
- `ActionGerarRespostaComIA`
- `ActionBuscarUltimosAvisos`
- `ActionBuscarCronograma`
- `ActionBuscarDataAvaliacao`
- `ActionBuscarInfoAtividadeAcademica`
- `ActionBuscarAtendimentoDocente`
- `ActionBuscarInfoDocente`
- `ActionBuscarMaterial`

**Teste:**
- Fazer perguntas e verificar se são salvas no banco
- Verificar se tópicos são extraídos corretamente

---

### 2.2 Retornar URLs de Documentos Quando Solicitado

**Requisito:** 
- Quando aluno pedir documento, retornar URLs dos documentos
- Quando aluno perguntar sobre base de conhecimento usada, retornar URLs dos documentos de referência

**Descoberta Importante:**
A API tem endpoint `/ia/testar-baseconhecimento?q={termo}` que retorna:
```json
{
  "query": "...",
  "quantidade_contextos": 5,
  "contextos": [...],
  "documentos_encontrados": 3,
  "urls_documentos": ["https://...", "https://..."]
}
```

**✅ SOLUÇÃO:** Usar esse endpoint para buscar documentos com URLs!

**Implementação:**

#### Solução: Usar Endpoint de Teste da IA (Implementar Agora)

Modificar `/baseconhecimento/get_buscar` para também retornar URLs quando solicitado:
```python
# Na API (NÃO MODIFICAR - apenas documentar)
@router.get("/get_buscar")
async def buscar_conhecimento(
    q: str,
    incluir_urls: bool = False  # Novo parâmetro
):
    # ... busca atual ...
    if incluir_urls:
        return {
            "contextos": [...],
            "documentos": [
                {
                    "nome_arquivo_origem": "...",
                    "url_documento": "...",
                    "categoria": "..."
                }
            ]
        }
```

#### Opção 2: Criar Endpoint Específico (Recomendado - mas precisa modificar API)

Criar `GET /baseconhecimento/disciplina_nome/{nome_disciplina}` que retorna documentos com URLs.

#### Opção 3: Solução no Rasa Usando Endpoint de Teste (Implementar Agora)

A API tem endpoint de teste `/ia/testar-baseconhecimento` que retorna documentos com URLs! Podemos usar isso.

**Implementação:**
```python
# Modificar ActionBuscarMaterial para retornar URLs
class ActionBuscarMaterial(Action):
    def name(self) -> Text:
        return "action_buscar_material"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disciplina_nome = tracker.get_slot("disciplina")
        
        if not disciplina_nome:
            dispatcher.utter_message(text="Claro. De qual disciplina você quer o material?")
            return []
        
        dispatcher.utter_message(text=f"Buscando materiais para {disciplina_nome}...")

        try:
            # SOLUÇÃO: Usar endpoint de teste que retorna documentos com URLs
            response = requests.get(
                f"{API_URL}/ia/testar-baseconhecimento",
                params={"q": disciplina_nome},
                timeout=10
            )
            response.raise_for_status()
            
            dados = response.json()
            documentos_encontrados = dados.get("documentos_encontrados", 0)
            urls_documentos = dados.get("urls_documentos", [])
            
            if documentos_encontrados > 0 and urls_documentos:
                mensagem = f"Encontrei {documentos_encontrados} documento(s) para {disciplina_nome}:\n\n"
                for i, url in enumerate(urls_documentos[:5], 1):  # Limita a 5 documentos
                    mensagem += f"{i}. {url}\n"
                
                if documentos_encontrados > 5:
                    mensagem += f"\n... e mais {documentos_encontrados - 5} documento(s)."
                
                dispatcher.utter_message(text=mensagem)
            else:
                # Fallback: usar busca geral
                response_fallback = requests.get(
                    f"{API_URL}/baseconhecimento/get_buscar",
                    params={"q": disciplina_nome},
                    timeout=10
                )
                if response_fallback.ok:
                    dados_fallback = response_fallback.json()
                    contextos = dados_fallback.get("contextos", [])
                    if contextos:
                        dispatcher.utter_message(
                            text=f"Encontrei informações sobre {disciplina_nome}, mas os documentos não estão disponíveis para download direto. "
                                 f"Consulte o painel administrativo para acessar os arquivos."
                        )
                    else:
                        dispatcher.utter_message(text=f"Não encontrei materiais para {disciplina_nome} no sistema.")
                else:
                    dispatcher.utter_message(text=f"Não encontrei materiais para {disciplina_nome} no sistema.")

        except Exception as e:
            print(f"Erro ao buscar documentos: {e}")
            dispatcher.utter_message(text="Erro ao conectar ao sistema de documentos.")
        
        return [SlotSet("disciplina", None)]
```

**✅ VANTAGEM:** O endpoint `/ia/testar-baseconhecimento` já retorna URLs dos documentos!

**Arquivos a modificar:**
- `actions/actions.py` - Modificar `ActionBuscarMaterial`

**Recomendação para API:**
Criar `GET /baseconhecimento/disciplina/{disciplina_id}` que retorna documentos com URLs.

**Arquivos a modificar:**
- `actions/actions.py` - Nova action `ActionBuscarDocumentosComURL`
- `domain.yml` - Adicionar nova action
- `data/rules.yml` - Adicionar regra para quando perguntar sobre documentos/base

---

### 2.3 Implementar Sistema de Dúvidas Frequentes por Categorias

**Requisito:**
- Dúvidas divididas em: "Dúvidas Institucionais" e "Dúvidas de Conteúdo"
- Dúvidas Institucionais: Informações manuais do painel
- Dúvidas de Conteúdo: Dos documentos processados (usar palavras-chave do Gemini)
- Mostrar categorias mais perguntadas, não dúvidas individuais

**Estrutura de Dados:**

A base de conhecimento já tem:
- `categoria` - Categoria do documento (ex: "Artigo", "Slides", etc.)
- `palavra_chave` - Lista de palavras-chave extraídas pelo Gemini
- `id_disciplina` - Disciplina relacionada

**Implementação:**

#### 2.3.1 Criar Action para Buscar Categorias de Dúvidas Frequentes

```python
class ActionBuscarDuvidasFrequentes(Action):
    def name(self) -> Text:
        return "action_buscar_duvidas_frequentes"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Busca e retorna categorias de dúvidas frequentes.
        Agrupa por tipo (Institucional vs Conteúdo) e por categoria/palavras-chave.
        """
        try:
            # 1. Buscar todas as mensagens dos alunos (perguntas salvas)
            response_msg = requests.get(
                f"{API_URL}/mensagens_aluno/get_lista_msg/",
                timeout=10
            )
            
            if not response_msg.ok:
                dispatcher.utter_message(text="Erro ao buscar dúvidas frequentes.")
                return []
            
            mensagens = response_msg.json()
            
            # 2. Agrupar por tópicos
            topicos_contagem = {}
            for msg in mensagens:
                topicos = msg.get('topico', [])
                for topico in topicos:
                    topicos_contagem[topico] = topicos_contagem.get(topico, 0) + 1
            
            # 3. Separar em Institucionais e Conteúdo
            duvidas_institucionais = {}
            duvidas_conteudo = {}
            
            topicos_institucionais = ["TCC", "APS", "Estágio", "Horas Complementares", "Aviso", "Docente"]
            topicos_conteudo = []  # Será preenchido com categorias da base de conhecimento
            
            for topico, count in sorted(topicos_contagem.items(), key=lambda x: x[1], reverse=True):
                if topico in topicos_institucionais:
                    duvidas_institucionais[topico] = count
                else:
                    duvidas_conteudo[topico] = count
            
            # 4. Buscar categorias da base de conhecimento (dúvidas de conteúdo)
            response_base = requests.get(
                f"{API_URL}/baseconhecimento/get_buscar",
                params={"q": ""},  # Busca geral para pegar todas as categorias
                timeout=10
            )
            
            # 5. Agrupar categorias mais frequentes da base de conhecimento
            # (Isso requer endpoint específico na API ou busca direta)
            
            # 6. Montar resposta
            mensagem = "📚 **Dúvidas Frequentes por Categoria:**\n\n"
            
            if duvidas_institucionais:
                mensagem += "🏛️ **Dúvidas Institucionais:**\n"
                for topico, count in list(duvidas_institucionais.items())[:5]:
                    mensagem += f"  • {topico}: {count} pergunta(s)\n"
                mensagem += "\n"
            
            if duvidas_conteudo:
                mensagem += "📖 **Dúvidas de Conteúdo:**\n"
                for topico, count in list(duvidas_conteudo.items())[:5]:
                    mensagem += f"  • {topico}: {count} pergunta(s)\n"
            
            dispatcher.utter_message(text=mensagem)
            
        except Exception as e:
            print(f"Erro ao buscar dúvidas frequentes: {e}")
            dispatcher.utter_message(text="Erro ao buscar dúvidas frequentes.")
        
        return []
```

**⚠️ LIMITAÇÃO:** 
- Endpoint `/baseconhecimento/get_buscar` não retorna todas as categorias
- Precisa de endpoint específico para agrupar por categorias/palavras-chave

**Observação Importante:**
A tabela `baseconhecimento` no Supabase tem o campo `url_documento`, mas:
- O schema Pydantic (`BaseConhecimento`) não inclui esse campo
- O endpoint `/baseconhecimento/get_buscar` não retorna esse campo (apenas `contextos`)
- O endpoint `/baseconhecimento/get_baseconhecimento_id/{id}` retorna o registro completo (incluindo `url_documento`)

**Solução:** Criar endpoint específico ou modificar o existente para retornar documentos com URLs.

#### 2.3.2 Melhorar Classificação Usando Palavras-Chave do Gemini

**Conceito Importante:**
- **Dúvidas Institucionais:** Informações manuais do painel (TCC, APS, Estágio, etc.)
- **Dúvidas de Conteúdo:** Dos documentos processados - usar `palavra_chave` e `categoria` da base de conhecimento

A base de conhecimento já armazena `palavra_chave` extraídas pelo Gemini quando processa documentos. Podemos usar isso para classificar dúvidas de conteúdo automaticamente.

**Estratégia:**
1. Quando salvar pergunta, verificar se há correspondência com palavras-chave da base de conhecimento
2. Se houver, classificar como "Dúvida de Conteúdo" e associar categoria/palavras-chave
3. Se não houver, classificar como "Dúvida Institucional" baseado nos tópicos extraídos

**Implementação Melhorada:**
```python
class ActionBuscarDuvidasFrequentes(Action):
    def name(self) -> Text:
        return "action_buscar_duvidas_frequentes"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        Busca e retorna categorias de dúvidas frequentes.
        Agrupa por tipo (Institucional vs Conteúdo) e por categoria/palavras-chave.
        """
        try:
            # 1. Buscar todas as mensagens dos alunos
            response_msg = requests.get(
                f"{API_URL}/mensagens_aluno/get_lista_msg/",
                timeout=10
            )
            
            if not response_msg.ok:
                dispatcher.utter_message(text="Erro ao buscar dúvidas frequentes.")
                return []
            
            mensagens = response_msg.json()
            
            # 2. Agrupar perguntas por tópicos (Dúvidas Institucionais)
            topicos_institucionais = {
                "TCC": 0,
                "APS": 0,
                "Estágio": 0,
                "Horas Complementares": 0,
                "Aviso": 0,
                "Docente": 0,
                "Disciplina": 0
            }
            
            for msg in mensagens:
                topicos = msg.get('topico', [])
                for topico in topicos:
                    if topico in topicos_institucionais:
                        topicos_institucionais[topico] += 1
            
            # 3. Buscar categorias e palavras-chave da base de conhecimento (Dúvidas de Conteúdo)
            categorias_conteudo = {}
            palavras_chave_frequentes = {}
            
            # Buscar todas as mensagens classificadas como "Conteúdo"
            mensagens_conteudo = [msg for msg in mensagens if "Conteúdo" in msg.get('topico', [])]
            
            # Agrupar por palavras-chave mais frequentes nas perguntas de conteúdo
            for msg in mensagens_conteudo:
                pergunta = msg.get('primeira_pergunta', '').lower()
                
                # Extrair palavras-chave da pergunta (palavras com mais de 4 caracteres)
                palavras = [p for p in pergunta.split() if len(p) > 4]
                for palavra in palavras:
                    palavras_chave_frequentes[palavra] = palavras_chave_frequentes.get(palavra, 0) + 1
            
            # NOTA: Para agrupar por categorias da base de conhecimento (ex: "Algoritmos", "Banco de Dados"),
            # precisaríamos de um endpoint que retorne essas informações agrupadas.
            # Por enquanto, agrupamos por palavras-chave das perguntas.
            
            # 4. Montar resposta
            mensagem = "📚 **Dúvidas Frequentes por Categoria:**\n\n"
            
            # Dúvidas Institucionais
            duvidas_inst = {k: v for k, v in topicos_institucionais.items() if v > 0}
            if duvidas_inst:
                mensagem += "🏛️ **Dúvidas Institucionais:**\n"
                for topico, count in sorted(duvidas_inst.items(), key=lambda x: x[1], reverse=True)[:5]:
                    mensagem += f"  • {topico}: {count} pergunta(s)\n"
                mensagem += "\n"
            
            # Dúvidas de Conteúdo (palavras-chave mais frequentes)
            if palavras_chave_frequentes:
                mensagem += "📖 **Dúvidas de Conteúdo (Tópicos mais perguntados):**\n"
                for palavra, count in sorted(palavras_chave_frequentes.items(), key=lambda x: x[1], reverse=True)[:5]:
                    mensagem += f"  • {palavra.title()}: {count} pergunta(s)\n"
            
            if not duvidas_inst and not palavras_chave_frequentes:
                mensagem += "Ainda não há dúvidas frequentes registradas."
            
            dispatcher.utter_message(text=mensagem)
            
        except Exception as e:
            print(f"Erro ao buscar dúvidas frequentes: {e}")
            dispatcher.utter_message(text="Erro ao buscar dúvidas frequentes.")
        
        return []
```

**⚠️ LIMITAÇÃO:** 
- Endpoint `/baseconhecimento/get_buscar` não retorna todas as categorias
- Precisa de endpoint específico para agrupar por categorias/palavras-chave da base de conhecimento

**Recomendação para API:**
Criar endpoint `GET /baseconhecimento/categorias_frequentes` que retorna:
```json
{
  "categorias_conteudo": [
    {"categoria": "Algoritmos", "quantidade": 15},
    {"categoria": "Banco de Dados", "quantidade": 12}
  ],
  "palavras_chave_frequentes": [
    {"palavra": "UML", "quantidade": 8},
    {"palavra": "Scrum", "quantidade": 6}
  ]
}
```

**Arquivos a modificar:**
- `actions/actions.py` - Nova action `ActionBuscarDuvidasFrequentes`
- `domain.yml` - Adicionar intent `consultar_duvidas_frequentes` e action
- `data/nlu.yml` - Adicionar exemplos:
  ```yaml
  - intent: consultar_duvidas_frequentes
    examples: |
      - quais sao as duvidas mais frequentes
      - o que os alunos mais perguntam
      - duvidas frequentes
      - categorias mais perguntadas
      - quais sao os topicos mais consultados
      - o que e mais perguntado
  ```
- `data/rules.yml` - Adicionar regra:
  ```yaml
  - rule: Consultar duvidas frequentes
    steps:
    - intent: consultar_duvidas_frequentes
    - action: action_buscar_duvidas_frequentes
  ```

---

## 🚀 FASE 3: MELHORIAS E OTIMIZAÇÕES (Semana 3-4)

### 3.1 Implementar Cache de Requisições

**Implementação:**
```python
# Adicionar classe CacheHelper em actions/actions.py
class CacheHelper:
    _cache_disciplinas = {}
    _cache_professores = {}
    _cache_timestamp = {}
    CACHE_TTL = 300  # 5 minutos
    
    @staticmethod
    def get_disciplina_id(disciplina_nome: str) -> str | None:
        # ... implementação completa no documento OTIMIZACOES_BASEADAS_TCC.md
        pass
```

**Arquivos:**
- `actions/actions.py` - Adicionar classe `CacheHelper`
- Modificar `get_disciplina_id_by_name` para usar cache

---

### 3.2 Implementar Validação de Dados

**Implementação:**
```python
# Adicionar classes ErrorHandler e ResponseValidator
# Ver código completo em OTIMIZACOES_BASEADAS_TCC.md
```

**Arquivos:**
- `actions/actions.py` - Adicionar classes de validação
- Modificar todas as actions para usar validação

---

### 3.3 Adicionar Logging Estruturado

**Implementação:**
```python
# Adicionar ActionLogger
# Ver código completo em OTIMIZACOES_BASEADAS_TCC.md
```

**Arquivos:**
- `actions/actions.py` - Adicionar logging
- Modificar todas as actions para logar

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Correções Críticas (URGENTE)
- [ ] Corrigir `get_disciplina_id_by_name` (usar endpoint de cronograma)
- [ ] Corrigir `ActionBuscarInfoAtividadeAcademica` (ler formato `{"contextos": [...]}`)
- [ ] Modificar `ActionBuscarMaterial` (usar busca alternativa)
- [ ] Testar todas as correções

### Fase 2: Novas Funcionalidades
- [ ] Implementar `salvar_pergunta_aluno()` e `extrair_topicos_da_pergunta()`
- [ ] Adicionar salvamento de perguntas em todas as actions principais
- [ ] Modificar `ActionBuscarMaterial` para usar `/ia/testar-baseconhecimento` e retornar URLs
- [ ] Modificar `ActionGerarRespostaComIA` para retornar URLs dos documentos de referência
- [ ] Criar `ActionBuscarDuvidasFrequentes`
- [ ] Adicionar intent `consultar_duvidas_frequentes` no NLU
- [ ] Adicionar regras para novas funcionalidades

### Fase 3: Otimizações
- [ ] Implementar `CacheHelper`
- [ ] Implementar `ErrorHandler` e `ResponseValidator`
- [ ] Implementar `ActionLogger`
- [ ] Adicionar stories de erro
- [ ] Melhorar contexto conversacional

---

## 🎯 PRIORIZAÇÃO

### 🔴 CRÍTICO (Fazer Primeiro):
1. Corrigir busca de disciplina por nome
2. Corrigir formato de resposta da base de conhecimento
3. Implementar salvamento de perguntas

### 🟡 IMPORTANTE (Fazer Depois):
4. Modificar `ActionBuscarMaterial` para retornar URLs usando `/ia/testar-baseconhecimento`
5. Modificar `ActionGerarRespostaComIA` para incluir URLs de referência
6. Implementar dúvidas frequentes por categorias
7. Implementar cache

### 🟢 DESEJÁVEL (Fazer Por Último):
8. Validação de dados
9. Logging estruturado
10. Melhorias de contexto

---

## 📊 ENDPOINTS NECESSÁRIOS NA API (Documentar)

### Endpoints que Seriam Úteis (mas não podemos modificar):

1. **`GET /disciplinas/get_id_por_nome/{nome_disciplina}`**
   - Retorna: `{"id_disciplina": "uuid", "nome_disciplina": "..."}`
   - Usa busca `.ilike()` para flexibilidade

2. **`GET /baseconhecimento/disciplina/{disciplina_id}`**
   - Retorna: `[{"nome_arquivo_origem": "...", "url_documento": "...", "categoria": "...", ...}]`
   - Lista documentos de uma disciplina com URLs

3. **`GET /baseconhecimento/disciplina_nome/{nome_disciplina}`**
   - Versão que busca por nome da disciplina
   - Retorna documentos com URLs

4. **`GET /baseconhecimento/categorias_frequentes`**
   - Retorna categorias e palavras-chave mais frequentes
   - Agrupado por tipo (Institucional vs Conteúdo)

5. **`GET /baseconhecimento/get_buscar` (Modificar)**
   - Adicionar parâmetro `incluir_urls: bool = False`
   - Quando `True`, retorna também `url_documento` nos resultados

---

## 🧪 TESTES NECESSÁRIOS

### Testes de Integração:
- [ ] Testar busca de disciplina por nome
- [ ] Testar salvamento de perguntas
- [ ] Testar busca de documentos
- [ ] Testar dúvidas frequentes

### Testes de Funcionalidade:
- [ ] Verificar se todas as perguntas são salvas
- [ ] Verificar se tópicos são extraídos corretamente
- [ ] Verificar se URLs são retornadas quando disponíveis
- [ ] Verificar se categorias são agrupadas corretamente

---

## 📅 CRONOGRAMA SUGERIDO

### Semana 1: Correções Críticas
- **Dia 1-2:** Corrigir busca de disciplina e formato de resposta
- **Dia 3-4:** Implementar salvamento de perguntas
- **Dia 5:** Testes e ajustes

### Semana 2: Novas Funcionalidades
- **Dia 1-2:** Implementar busca de documentos (temporária)
- **Dia 3-4:** Implementar dúvidas frequentes
- **Dia 5:** Testes e ajustes

### Semana 3: Otimizações
- **Dia 1-2:** Implementar cache
- **Dia 3-4:** Implementar validação e logging
- **Dia 5:** Testes finais

---

## ⚠️ DEPENDÊNCIAS E LIMITAÇÕES

### Dependências da API:
- Algumas funcionalidades requerem novos endpoints na API
- Documentar necessidade de endpoints para implementação completa

### Limitações Atuais:
- Busca de documentos limitada (sem endpoint específico)
- Dúvidas frequentes de conteúdo limitadas (sem agrupamento na API)
- URLs de documentos não retornadas diretamente

### Soluções Temporárias:
- Usar endpoints existentes de forma criativa
- Implementar lógica no Rasa quando possível
- Documentar necessidade de endpoints na API

---

---

## 📚 REFERÊNCIAS

Este plano foi criado com base em:
- `ANALISE_PROJETO_RASA.md` - Análise inicial completa
- `OTIMIZACOES_BASEADAS_TCC.md` - 12 otimizações detalhadas
- `ANALISE_INTEGRACAO_RASA_API.md` - Análise de integração
- `RESUMO_PROBLEMAS_CRITICOS_API.md` - Problemas críticos
- Estrutura real da API FastAPI em `D:/ChatBot_API`

---

## ✅ PRÓXIMOS PASSOS IMEDIATOS

1. **Revisar este plano** e validar prioridades
2. **Começar pela Fase 1** (Correções Críticas)
3. **Testar cada implementação** antes de prosseguir
4. **Documentar endpoints necessários** na API para implementação completa

---

**Documento criado em:** 2025-01-27
**Baseado em:** Análise completa dos documentos em `propostas_cursor/` e estrutura real da API
**Status:** ✅ Pronto para implementação

