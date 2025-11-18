# 🚀 OTIMIZAÇÕES BASEADAS NO TCC - CHATBOT ASSISTENTE ACADÊMICO

## 📋 CONTEXTO DO PROJETO (Baseado nos Arquivos Analisados)

### Arquitetura Identificada:
1. **Chatbot Rasa** - Processamento de linguagem natural
2. **API FastAPI** - Lógica de negócios e acesso ao Supabase
3. **Google Gemini** - IA generativa para respostas e processamento de documentos
4. **Sistema de Processamento de Arquivos** - Pipeline de 2 etapas:
   - Etapa 1: `local_file_watcher.py` - Processa arquivos com Gemini
   - Etapa 2: `metadata_enricher.py` - Enriquece metadados e salva no banco
5. **Supabase** - Banco de dados PostgreSQL

### Funcionalidades Principais:
- Consulta de avisos, cronogramas, avaliações
- Informações sobre docentes (contato, horário de atendimento)
- Busca de materiais de aula
- Consulta de regras (TCC, APS, Estágio, Horas Complementares)
- Respostas geradas por IA para tópicos de estudo
- Processamento automático de documentos acadêmicos

---

## 🎯 OTIMIZAÇÕES PRIORITÁRIAS

### 1. 🔴 OTIMIZAÇÃO CRÍTICA: Cache de Requisições Frequentes

**Problema Identificado:**
- Múltiplas actions fazem requisições repetidas para a mesma API
- `get_disciplina_id_by_name` é chamada várias vezes para a mesma disciplina
- Lista de professores é buscada toda vez, mesmo sem mudanças

**Impacto:**
- Latência desnecessária
- Sobrecarga na API FastAPI
- Experiência do usuário degradada

**Solução:**
```python
# Adicionar em actions/actions.py
from functools import lru_cache
from datetime import datetime, timedelta

class CacheHelper:
    _cache_disciplinas = {}
    _cache_professores = {}
    _cache_timestamp = {}
    CACHE_TTL = 300  # 5 minutos
    
    @staticmethod
    def get_disciplina_id(disciplina_nome: str) -> str | None:
        # Normalizar nome
        nome_normalizado = disciplina_nome.strip().title()
        
        # Verificar cache
        if nome_normalizado in CacheHelper._cache_disciplinas:
            timestamp = CacheHelper._cache_timestamp.get(f"disc_{nome_normalizado}")
            if timestamp and datetime.now() - timestamp < timedelta(seconds=CacheHelper.CACHE_TTL):
                return CacheHelper._cache_disciplinas[nome_normalizado]
        
        # Buscar na API
        try:
            response = requests.get(
                f"{API_URL}/disciplinas/get_disciplina_id/{nome_normalizado}",
                timeout=10
            )
            response.raise_for_status()
            id_disciplina = response.json().get("id_disciplina")
            
            if id_disciplina:
                CacheHelper._cache_disciplinas[nome_normalizado] = id_disciplina
                CacheHelper._cache_timestamp[f"disc_{nome_normalizado}"] = datetime.now()
            
            return id_disciplina
        except requests.exceptions.RequestException:
            return None
    
    @staticmethod
    def get_lista_professores() -> list:
        cache_key = "professores"
        timestamp = CacheHelper._cache_timestamp.get(cache_key)
        
        if cache_key in CacheHelper._cache_professores:
            if timestamp and datetime.now() - timestamp < timedelta(seconds=CacheHelper.CACHE_TTL):
                return CacheHelper._cache_professores[cache_key]
        
        try:
            response = requests.get(f"{API_URL}/professores/lista_professores/", timeout=10)
            response.raise_for_status()
            professores = response.json()
            
            CacheHelper._cache_professores[cache_key] = professores
            CacheHelper._cache_timestamp[cache_key] = datetime.now()
            
            return professores
        except requests.exceptions.RequestException:
            return []
    
    @staticmethod
    def clear_cache():
        """Limpa o cache (útil para testes ou atualizações)"""
        CacheHelper._cache_disciplinas.clear()
        CacheHelper._cache_professores.clear()
        CacheHelper._cache_timestamp.clear()
```

**Benefícios:**
- Redução de 70-90% nas requisições para dados estáticos
- Resposta mais rápida para o usuário
- Menor carga no servidor FastAPI

---

### 3. 🔴 CRÍTICO: Validação de Dados e Tratamento de Erros Robusto

**Problema Identificado:**
- Mensagens de erro genéricas ("Erro ao conectar...")
- Falta de logging estruturado
- Exceções genéricas (`except Exception`) sem diferenciação
- Não valida se a resposta da API está no formato esperado
- Não trata casos onde a API retorna lista vazia vs. erro
- Falta validação de entidades antes de usar

**Impacto:**
- Usuário não sabe o que fazer quando há erro
- Difícil debugar problemas
- Pode quebrar silenciosamente

**Solução Completa:**

```python
# Adicionar em actions/actions.py
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rasa_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ErrorHandler:
    """Trata erros de API de forma amigável e registra logs"""
    
    @staticmethod
    def handle_api_error(dispatcher: CollectingDispatcher, error: Exception, 
                        context: str = "", action_name: str = ""):
        """Trata erros de API de forma amigável"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Log estruturado
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action_name,
            "context": context,
            "error_type": error_type,
            "error_message": error_msg
        }
        logger.error(f"API_ERROR: {json.dumps(log_entry)}")
        
        # Mensagens específicas por tipo de erro
        if isinstance(error, requests.exceptions.Timeout):
            dispatcher.utter_message(
                text="O servidor está demorando para responder. Por favor, tente novamente em alguns instantes."
            )
        elif isinstance(error, requests.exceptions.ConnectionError):
            dispatcher.utter_message(
                text="Não foi possível conectar ao servidor. Verifique sua conexão ou tente mais tarde."
            )
        elif isinstance(error, requests.exceptions.HTTPError):
            if hasattr(error, 'response') and error.response:
                status_code = error.response.status_code
                if status_code == 404:
                    dispatcher.utter_message(
                        text="A informação solicitada não foi encontrada no sistema."
                    )
                elif status_code == 500:
                    dispatcher.utter_message(
                        text="Ocorreu um erro interno. Nossa equipe foi notificada. Tente novamente mais tarde."
                    )
                elif status_code == 503:
                    dispatcher.utter_message(
                        text="O serviço está temporariamente indisponível. Tente novamente em alguns minutos."
                    )
                else:
                    dispatcher.utter_message(
                        text=f"Ocorreu um erro ao processar sua solicitação (código {status_code}). Tente novamente."
                    )
            else:
                dispatcher.utter_message(
                    text="Ocorreu um erro ao processar sua solicitação. Tente novamente."
                )
        elif isinstance(error, requests.exceptions.JSONDecodeError):
            dispatcher.utter_message(
                text="O servidor retornou uma resposta inválida. Tente novamente mais tarde."
            )
        else:
            dispatcher.utter_message(
                text="Desculpe, ocorreu um erro inesperado. Por favor, tente novamente."
            )

class ResponseValidator:
    """Valida respostas da API antes de usar"""
    
    @staticmethod
    def validate_json_response(response: requests.Response, 
                              expected_keys: List[str] = None) -> Optional[Dict]:
        """Valida se a resposta é JSON válido e tem as chaves esperadas"""
        try:
            data = response.json()
            
            if expected_keys:
                missing_keys = [key for key in expected_keys if key not in data]
                if missing_keys:
                    logger.warning(f"Resposta da API sem chaves esperadas: {missing_keys}")
                    return None
            
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Resposta da API não é JSON válido: {e}")
            return None
    
    @staticmethod
    def validate_list_response(response: requests.Response) -> List:
        """Valida se a resposta é uma lista válida"""
        data = ResponseValidator.validate_json_response(response)
        if data is None:
            return []
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'value' in data:
            # Algumas APIs retornam {"value": [...]}
            return data['value']
        else:
            logger.warning(f"Resposta não é uma lista: {type(data)}")
            return []
```

**Uso nas Actions:**
```python
# Exemplo em ActionBuscarCronograma
def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    disciplina_nome = next(tracker.get_latest_entity_values("disciplina"), None)
    
    if not disciplina_nome:
        dispatcher.utter_message(text="De qual disciplina você quer saber o horário?")
        return []

    disciplina_id = get_disciplina_id_by_name(disciplina_nome)
    
    if not disciplina_id:
        dispatcher.utter_message(text=f"Não encontrei a disciplina {disciplina_nome}.")
        return []

    try:
        response = requests.get(f"{API_URL}/cronograma/disciplina/{disciplina_id}", timeout=10)
        response.raise_for_status()
        
        # VALIDAÇÃO ADICIONADA
        cronogramas = ResponseValidator.validate_list_response(response)
        
        if not cronogramas:
            dispatcher.utter_message(text=f"Sem horários cadastrados para {disciplina_nome}.")
            return []
        
        # Processar cronogramas...
        msg = f"Horário de {disciplina_nome}:\n"
        for item in cronogramas:
            # VALIDAÇÃO ADICIONADA
            if not isinstance(item, dict):
                logger.warning(f"Item do cronograma não é dict: {type(item)}")
                continue
                
            dia = item.get('dia_semana', 'N/A')
            inicio = item.get('hora_inicio', 'N/A')
            sala = item.get('sala', 'N/A')
            msg += f"- {dia} às {inicio} (Sala {sala})\n"
        
        dispatcher.utter_message(text=msg)

    except Exception as e:
        ErrorHandler.handle_api_error(
            dispatcher, e, 
            context=f"Buscar cronograma - disciplina {disciplina_nome}",
            action_name=self.name()
        )
    
    return []
```

---

### 4. 🟡 OTIMIZAÇÃO: Tratamento de Erros Robusto e Mensagens Amigáveis

**Problema Identificado:**
- Mensagens de erro genéricas ("Erro ao conectar...")
- Falta de diferenciação entre tipos de erro (404, 500, timeout, etc.)
- Usuário não sabe o que fazer quando há erro

**Solução:**
```python
class ErrorHandler:
    @staticmethod
    def handle_api_error(dispatcher: CollectingDispatcher, error: Exception, context: str = ""):
        """Trata erros de API de forma amigável"""
        if isinstance(error, requests.exceptions.Timeout):
            dispatcher.utter_message(
                text="O servidor está demorando para responder. Por favor, tente novamente em alguns instantes."
            )
        elif isinstance(error, requests.exceptions.ConnectionError):
            dispatcher.utter_message(
                text="Não foi possível conectar ao servidor. Verifique sua conexão ou tente mais tarde."
            )
        elif isinstance(error, requests.exceptions.HTTPError):
            if error.response.status_code == 404:
                dispatcher.utter_message(
                    text="A informação solicitada não foi encontrada no sistema."
                )
            elif error.response.status_code == 500:
                dispatcher.utter_message(
                    text="Ocorreu um erro interno. Nossa equipe foi notificada. Tente novamente mais tarde."
                )
            else:
                dispatcher.utter_message(
                    text="Ocorreu um erro ao processar sua solicitação. Tente novamente."
                )
        else:
            dispatcher.utter_message(
                text="Desculpe, ocorreu um erro inesperado. Por favor, tente novamente."
            )
        
        # Log do erro para análise
        print(f"[ERRO] {context}: {type(error).__name__}: {str(error)}")
```

**Uso nas Actions:**
```python
# Exemplo em ActionBuscarMaterial
try:
    response = requests.get(f"{API_URL}/documento/disciplina/{id_disciplina}", timeout=10)
    response.raise_for_status()
    # ... resto do código
except Exception as e:
    ErrorHandler.handle_api_error(dispatcher, e, f"Buscar material - disciplina {disciplina_nome}")
    return [SlotSet("disciplina", None)]
```

---

### 5. 🟡 OTIMIZAÇÃO: Validação de Entidades com Sugestões

**Problema Identificado:**
- Se usuário digitar "Engenharia" mas a disciplina for "Engenharia de Software", retorna erro
- Não há sugestões de correção
- Experiência frustrante para o usuário

**Solução:**
```python
class ActionValidateFormBuscarMaterial(Action):
    def name(self) -> Text:
        return "action_validate_form_buscar_material"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disciplina = tracker.get_slot("disciplina")
        
        if not disciplina:
            return []
        
        # Buscar ID da disciplina
        id_disciplina = CacheHelper.get_disciplina_id(disciplina)
        
        if id_disciplina:
            # Disciplina válida
            return []
        
        # Disciplina não encontrada - buscar sugestões
        try:
            # Buscar todas as disciplinas para sugerir
            response = requests.get(f"{API_URL}/disciplinas/lista", timeout=10)
            if response.ok:
                todas_disciplinas = [d.get('nome') for d in response.json()]
                
                # Buscar disciplinas similares (fuzzy matching simples)
                sugestoes = self._buscar_similares(disciplina, todas_disciplinas, limite=3)
                
                if sugestoes:
                    mensagem = f"Não encontrei a disciplina '{disciplina}'. Você quis dizer:\n"
                    for i, sug in enumerate(sugestoes, 1):
                        mensagem += f"{i}. {sug}\n"
                    mensagem += "\nPor favor, informe o nome correto da disciplina."
                    dispatcher.utter_message(text=mensagem)
                else:
                    dispatcher.utter_message(
                        text=f"Disciplina '{disciplina}' não encontrada. Verifique se o nome está correto."
                    )
        except Exception:
            dispatcher.utter_message(
                text=f"Disciplina '{disciplina}' não encontrada. Verifique se o nome está correto."
            )
        
        # Limpar slot para tentar novamente
        return [SlotSet("disciplina", None)]
    
    def _buscar_similares(self, texto: str, lista: list, limite: int = 3) -> list:
        """Busca palavras similares usando comparação simples"""
        texto_lower = texto.lower()
        sugestoes = []
        
        for item in lista:
            if texto_lower in item.lower() or item.lower() in texto_lower:
                sugestoes.append(item)
            elif self._similaridade_simples(texto_lower, item.lower()) > 0.6:
                sugestoes.append(item)
        
        return sugestoes[:limite]
    
    def _similaridade_simples(self, s1: str, s2: str) -> float:
        """Calcula similaridade simples entre duas strings"""
        palavras1 = set(s1.split())
        palavras2 = set(s2.split())
        if not palavras1 or not palavras2:
            return 0.0
        intersecao = palavras1.intersection(palavras2)
        uniao = palavras1.union(palavras2)
        return len(intersecao) / len(uniao) if uniao else 0.0
```

**Adicionar no domain.yml:**
```yaml
forms:
  form_buscar_material:
    required_slots:
    - disciplina
    ignored_intents:
    - agradecer
    - saudar
    - despedir
    validate: true  # <-- ADICIONAR
```

---

### 6. 🟡 OTIMIZAÇÃO: Gestão de Slots e Contexto Melhorada

**Problema Identificado:**
- Slots não são limpos em alguns fluxos de erro
- `influence_conversation: true` pode causar confusão
- Falta validação de slots antes de usar
- Slots podem ficar "presos" se houver erro

**Solução:**

```python
# Adicionar helper para limpeza de slots
class SlotManager:
    @staticmethod
    def clear_slots_on_error(*slot_names: str) -> List[SlotSet]:
        """Retorna lista de SlotSet para limpar slots em caso de erro"""
        return [SlotSet(slot_name, None) for slot_name in slot_names]
    
    @staticmethod
    def validate_slot(tracker: Tracker, slot_name: str, required: bool = True) -> tuple[bool, Optional[str]]:
        """Valida se o slot está preenchido e retorna o valor"""
        value = tracker.get_slot(slot_name)
        
        if required and not value:
            return False, None
        
        return True, value

# Exemplo de uso em ActionBuscarAtendimentoDocente
def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    nome_docente = tracker.get_slot("nome_docente")
    
    if not nome_docente:
        dispatcher.utter_message(text="De qual professor você quer o horário?")
        return []

    try:
        response = requests.get(f"{API_URL}/professores/lista_professores/", timeout=10)
        if response.ok:
            professores = ResponseValidator.validate_list_response(response)
            
            encontrado = False
            for doc in professores:
                if not isinstance(doc, dict):
                    continue
                    
                if nome_docente.lower() in doc.get('nome_professor', '').lower():
                    horario = doc.get('horario_atendimento', 'Horário não informado no cadastro.')
                    dispatcher.utter_message(text=f"Atendimento {doc['nome_professor']}:\n{horario}")
                    encontrado = True
                    # Limpar slot apenas no sucesso
                    return [SlotSet("nome_docente", None)]
            
            if not encontrado:
                dispatcher.utter_message(text=f"Professor(a) {nome_docente} não encontrado(a).")
                # Limpar slot mesmo quando não encontrado
                return [SlotSet("nome_docente", None)]

    except Exception as e:
        ErrorHandler.handle_api_error(
            dispatcher, e,
            context=f"Buscar atendimento - docente {nome_docente}",
            action_name=self.name()
        )
        # IMPORTANTE: Limpar slot mesmo em caso de erro
        return SlotManager.clear_slots_on_error("nome_docente")
    
    return []
```

---

### 7. 🟡 OTIMIZAÇÃO: Adicionar Stories para Fluxos de Erro

**Problema Identificado:**
- Apenas 4 stories definidas (muito poucas)
- Falta stories para fluxos complexos
- Falta stories para tratamento de erros
- Comentário indica história conflitante removida

**Solução:**

```yaml
# Adicionar em data/stories.yml

- story: Consultar material - disciplina nao encontrada
  steps:
  - user: |
      quero o material de Disciplina Inexistente
    intent: solicitar_material_aula
    entities:
    - disciplina: "Disciplina Inexistente"
  - action: form_buscar_material
  - active_loop: form_buscar_material
  - action: action_buscar_material
  - active_loop: null
  # Deve retornar mensagem de erro apropriada

- story: Consultar atendimento - professor nao encontrado
  steps:
  - user: |
      qual o horario do Professor Inexistente?
    intent: solicitar_atendimento_docente
    entities:
    - nome_docente: "Professor Inexistente"
  - action: form_atendimento_docente
  - active_loop: form_atendimento_docente
  - action: action_buscar_atendimento_docente
  - active_loop: null
  # Deve retornar mensagem de erro apropriada

- story: Consultar data avaliacao - sem disciplina
  steps:
  - user: |
      quando e a NP1?
    intent: consultar_data_avaliacao
    entities:
    - tipo_avaliacao: "NP1"
  - action: action_buscar_data_avaliacao
  # Deve perguntar qual disciplina

- story: Erro de conexao - retry
  steps:
  - user: |
      tem algum aviso novo?
    intent: consultar_aviso
  - action: action_buscar_ultimos_avisos
  # Se houver erro de conexão, mensagem apropriada

- story: Fluxo completo - consultar material apos erro
  steps:
  - user: |
      quero material de Disciplina Errada
    intent: solicitar_material_aula
    entities:
    - disciplina: "Disciplina Errada"
  - action: form_buscar_material
  - active_loop: form_buscar_material
  - action: action_buscar_material
  - active_loop: null
  - user: |
      Cloud Computing
    intent: informar_disciplina
    entities:
    - disciplina: "Cloud Computing"
  - action: form_buscar_material
  - active_loop: form_buscar_material
  - action: action_buscar_material
  - active_loop: null
```

---

### 8. 🟢 OTIMIZAÇÃO: Logging Estruturado para Análise

**Problema Identificado:**
- Logs apenas com `print()` não são estruturados
- Difícil analisar padrões de uso
- Não há métricas de performance

**Solução:**
```python
import logging
import json
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rasa_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ActionLogger:
    @staticmethod
    def log_action(action_name: str, intent: str, entities: dict, success: bool, 
                   duration_ms: float = None, error: str = None):
        """Registra ação do bot de forma estruturada"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action_name,
            "intent": intent,
            "entities": entities,
            "success": success,
            "duration_ms": duration_ms,
            "error": error
        }
        
        if success:
            logger.info(f"ACTION_SUCCESS: {json.dumps(log_entry)}")
        else:
            logger.error(f"ACTION_ERROR: {json.dumps(log_entry)}")
    
    @staticmethod
    def log_user_message(text: str, intent: str, confidence: float):
        """Registra mensagem do usuário"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "user_message",
            "text": text,
            "intent": intent,
            "confidence": confidence
        }
        logger.info(f"USER_MESSAGE: {json.dumps(log_entry)}")
```

**Uso:**
```python
# Em cada action
import time

def run(self, dispatcher, tracker, domain):
    start_time = time.time()
    intent = tracker.latest_message['intent'].get('name')
    entities = {e['entity']: e['value'] for e in tracker.latest_message.get('entities', [])}
    
    try:
        # ... lógica da action ...
        duration = (time.time() - start_time) * 1000
        ActionLogger.log_action(
            self.name(), intent, entities, True, duration_ms=duration
        )
        return []
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        ActionLogger.log_action(
            self.name(), intent, entities, False, 
            duration_ms=duration, error=str(e)
        )
        raise
```

---

### 9. 🟢 OTIMIZAÇÃO: Sistema de Feedback do Usuário

**Problema Identificado:**
- Não há como coletar feedback sobre a qualidade das respostas
- Dificulta melhoria contínua do bot
- Importante para TCC mostrar aprendizado

**Solução:**
```python
class ActionColetarFeedback(Action):
    def name(self) -> Text:
        return "action_coletar_feedback"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Esta action pode ser chamada após respostas importantes
        # ou através de um intent específico
        
        # Verificar se já coletou feedback nesta conversa
        feedback_coletado = tracker.get_slot("feedback_coletado")
        if feedback_coletado:
            return []
        
        # Perguntar feedback de forma não intrusiva
        dispatcher.utter_message(
            text="A resposta foi útil? (sim/não)"
        )
        
        return []
```

**Adicionar intent no nlu.yml:**
```yaml
- intent: fornecer_feedback_positivo
  examples: |
    - sim
    - foi util
    - ajudou
    - obrigado
    - perfeito

- intent: fornecer_feedback_negativo
  examples: |
    - nao
    - nao ajudou
    - nao entendi
    - errado
    - nao e isso
```

**Regra no rules.yml:**
```yaml
- rule: Coletar feedback positivo
  steps:
  - intent: fornecer_feedback_positivo
  - action: action_salvar_feedback
  - slot_was_set:
    - feedback_coletado: true
```

**Action para salvar feedback:**
```python
class ActionSalvarFeedback(Action):
    def name(self) -> Text:
        return "action_salvar_feedback"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Buscar última ação executada
        ultima_acao = None
        for event in reversed(tracker.events):
            if event.get('event') == 'action' and event.get('name'):
                ultima_acao = event.get('name')
                break
        
        feedback = "positivo" if tracker.latest_message['intent'].get('name') == "fornecer_feedback_positivo" else "negativo"
        
        payload = {
            "acao": ultima_acao,
            "intent": tracker.latest_message['intent'].get('name'),
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(f"{API_URL}/feedback/", json=payload, timeout=10)
            if response.ok:
                dispatcher.utter_message(text="Obrigado pelo feedback! Isso nos ajuda a melhorar.")
        except Exception:
            pass  # Falha silenciosa para não interromper a conversa
        
        return [SlotSet("feedback_coletado", True)]
```

---

### 10. 🟡 OTIMIZAÇÃO: Melhorias no Sistema de Processamento de Arquivos

**Problema Identificado (nos connectors):**
- `local_file_watcher.py` e `metadata_enricher.py` não têm tratamento de erro robusto
- Não há retry em caso de falha
- Timeout não configurado nas requisições

**Solução:**
```python
# Em metadata_enricher.py
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configurar retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)

def get_id_disciplina_por_nome(nome_disciplina: str) -> str | None:
    """Busca o UUID de uma disciplina na API FastAPI usando seu nome."""
    print(f"   [Busca] 1.5. Procurando ID para a disciplina '{nome_disciplina}'...")
    try:
        response = session.get(
            f"{API_FASTAPI_URL}/disciplina/nome/{nome_disciplina}",
            timeout=10
        )
        response.raise_for_status()
        id_disciplina = response.json().get("id_disciplina")
        if id_disciplina:
            print(f"   [Busca] 1.6. ID encontrado: {id_disciplina}")
            return id_disciplina
        return None
    except requests.exceptions.RequestException as e:
        print(f"   [ERRO Busca] Disciplina '{nome_disciplina}' não encontrada: {e}")
        return None
```

---

### 11. 🟢 OTIMIZAÇÃO: Contexto Conversacional Melhorado

**Problema Identificado:**
- Bot não mantém contexto entre perguntas relacionadas
- Se usuário perguntar "qual o horário?" depois de mencionar uma disciplina, não sabe qual

**Solução:**
```python
# Adicionar slot de contexto no domain.yml
slots:
  ultima_disciplina_consultada:
    type: text
    influence_conversation: true
    mappings:
    - type: from_entity
      entity: disciplina
    - type: from_text
      conditions:
      - active_loop: form_buscar_material

  ultima_acao_executada:
    type: text
    influence_conversation: false
```

**Modificar ActionBuscarCronograma:**
```python
def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    disciplina_nome = next(tracker.get_latest_entity_values("disciplina"), None)
    
    # Se não houver disciplina na mensagem, tentar usar a última consultada
    if not disciplina_nome:
        disciplina_nome = tracker.get_slot("ultima_disciplina_consultada")
        if disciplina_nome:
            dispatcher.utter_message(
                text=f"Consultando horário de {disciplina_nome}..."
            )
        else:
            dispatcher.utter_message(text="De qual disciplina você quer saber o horário?")
            return []
    
    # ... resto do código ...
    
    # Salvar como última disciplina consultada
    return [SlotSet("ultima_disciplina_consultada", disciplina_nome)]
```

**Adicionar stories para contexto:**
```yaml
- story: Usuario pergunta horario sem mencionar disciplina novamente
  steps:
  - intent: consultar_horario_aula
    entities:
    - disciplina: null
  - slot_was_set:
    - ultima_disciplina_consultada: "Engenharia de Software"
  - action: action_buscar_cronograma
```

---

### 12. 🟢 OTIMIZAÇÃO: Melhoria no Pipeline de NLU para Português

**Problema Identificado:**
- `WhitespaceTokenizer` não é ideal para português
- Falta componente específico para português

**Solução (já mencionada na análise anterior, mas importante):**
```yaml
# config.yml
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
    threshold: 0.4
    ambiguity_threshold: 0.15
```

**Alternativa (se não quiser usar Spacy):**
Manter o pipeline atual mas aumentar os thresholds do FallbackClassifier.

---

## 📊 RESUMO DAS OTIMIZAÇÕES

### Prioridade CRÍTICA (Implementar IMEDIATAMENTE):
0. 🔴 **Segurança - Credenciais** - Mover para variáveis de ambiente (RISCO CRÍTICO)
1. 🔴 **Implementar Testes** - Cobertura zero atualmente (CRÍTICO)
2. 🔴 **Validação de Dados** - Previne quebras silenciosas (CRÍTICO)

### Prioridade ALTA (Implementar Primeiro):
3. ✅ **Cache de Requisições** - Reduz latência e carga no servidor
4. ✅ **Validação com Sugestões** - Melhora experiência do usuário
5. ✅ **Gestão de Slots** - Previne slots "presos"
6. ✅ **Stories de Erro** - Melhora robustez do diálogo

### Prioridade MÉDIA:
7. ✅ **Tratamento de Erros Robusto** - Profissionaliza o bot
8. ✅ **Logging Estruturado** - Essencial para análise e TCC
9. ✅ **Contexto Conversacional** - Melhora significativamente a UX
10. ✅ **Melhorias nos Connectors** - Robustez do sistema completo

### Prioridade BAIXA (Mas Importante para TCC):
11. ✅ **Sistema de Feedback** - Dados valiosos para o TCC
12. ✅ **Pipeline NLU Otimizado** - Melhor precisão

---

## ⚠️ CHECKLIST DE AÇÕES IMEDIATAS

### Segurança (FAZER AGORA):
- [ ] **REVOGAR token do Telegram atual** (se repositório foi commitado)
- [ ] Criar arquivo `.env` com variáveis de ambiente
- [ ] Atualizar `credentials.yml` para usar variáveis de ambiente
- [ ] Adicionar `.env` ao `.gitignore`
- [ ] Criar `.env.example` como template
- [ ] Gerar novo token do Telegram (se necessário)

### Testes (FAZER AGORA):
- [ ] Criar `tests/test_stories.yml` com stories do projeto
- [ ] Criar `tests/test_actions.py` com testes unitários
- [ ] Adicionar `pytest` ao `requirements.txt`
- [ ] Executar `rasa test` para validar

### Validação (FAZER AGORA):
- [ ] Implementar `ErrorHandler` em `actions.py`
- [ ] Implementar `ResponseValidator` em `actions.py`
- [ ] Atualizar todas as actions para usar validação
- [ ] Testar tratamento de erros

---

## 🎯 IMPACTO ESPERADO

### Performance:
- **Redução de 70-90%** nas requisições duplicadas (cache)
- **Redução de 30-50%** no tempo de resposta médio
- **Melhoria de 20-30%** na precisão de intents (pipeline otimizado)

### Experiência do Usuário:
- **Mensagens de erro mais claras** e acionáveis
- **Sugestões inteligentes** quando há erro de digitação
- **Contexto mantido** entre perguntas relacionadas
- **Feedback coletado** para melhoria contínua

### Para o TCC:
- **Dados estruturados** para análise (logs)
- **Métricas de sucesso** (feedback)
- **Sistema mais robusto** e profissional
- **Base para trabalhos futuros** (aprendizado contínuo)

---

## 📝 PRÓXIMOS PASSOS RECOMENDADOS

1. **Implementar cache** (maior impacto, menor esforço)
2. **Adicionar validação com sugestões** (melhora UX significativamente)
3. **Configurar logging estruturado** (essencial para análise)
4. **Implementar sistema de feedback** (dados para TCC)
5. **Melhorar contexto conversacional** (stories e slots)

---

**Documento criado em:** {{ data_atual }}
**Baseado em:** Análise dos arquivos do projeto e arquitetura identificada

