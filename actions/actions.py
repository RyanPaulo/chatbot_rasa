import platform
import asyncio
from typing import Any, Text, Dict, List, Optional
from datetime import datetime, timedelta
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
from rasa_sdk.events import SlotSet
import logging
import json

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

API_URL = "http://127.0.0.1:8000"

# ===================================================================
# CONFIGURAÇÃO DE LOGGING
# ===================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rasa_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===================================================================
# CACHE HELPER
# ===================================================================
class CacheHelper:
    """Cache de requisições frequentes para melhorar performance"""
    _cache_disciplinas = {}
    _cache_professores = {}
    _cache_coordenadores = {}
    _cache_timestamp = {}
    CACHE_TTL = 300  # 5 minutos
    
    @staticmethod
    def get_disciplina_id(disciplina_nome: str) -> str | None:
        """
        Busca ID de disciplina com cache.
        Usa endpoint de cronograma que aceita nome.
        """
        # Normalizar nome
        nome_normalizado = disciplina_nome.strip()
        
        # Verificar cache
        if nome_normalizado in CacheHelper._cache_disciplinas:
            timestamp = CacheHelper._cache_timestamp.get(f"disc_{nome_normalizado}")
            if timestamp and datetime.now() - timestamp < timedelta(seconds=CacheHelper.CACHE_TTL):
                logger.info(f"Cache HIT: disciplina '{nome_normalizado}'")
                return CacheHelper._cache_disciplinas[nome_normalizado]
        
        # Buscar na API
        try:
            logger.info(f"Cache MISS: buscando disciplina '{nome_normalizado}' na API")
            response = requests.get(
                f"{API_URL}/disciplinas/get_diciplina_nome/{nome_normalizado}/cronograma",
                timeout=10
            )
            if response.ok:
                cronogramas = response.json()
                if cronogramas and isinstance(cronogramas, list) and len(cronogramas) > 0:
                    id_disciplina = cronogramas[0].get('id_disciplina')
                    if id_disciplina:
                        CacheHelper._cache_disciplinas[nome_normalizado] = id_disciplina
                        CacheHelper._cache_timestamp[f"disc_{nome_normalizado}"] = datetime.now()
                        logger.info(f"Cache SET: disciplina '{nome_normalizado}' -> {id_disciplina}")
                        return id_disciplina
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar disciplina '{nome_normalizado}': {e}")
            return None
    
    @staticmethod
    def get_lista_professores() -> list:
        """Busca lista de professores com cache"""
        cache_key = "professores"
        timestamp = CacheHelper._cache_timestamp.get(cache_key)
        
        if cache_key in CacheHelper._cache_professores:
            if timestamp and datetime.now() - timestamp < timedelta(seconds=CacheHelper.CACHE_TTL):
                logger.info("Cache HIT: lista de professores")
                return CacheHelper._cache_professores[cache_key]
        
        try:
            logger.info("Cache MISS: buscando lista de professores na API")
            response = requests.get(f"{API_URL}/professores/lista_professores/", timeout=10)
            response.raise_for_status()
            professores = response.json()
            
            CacheHelper._cache_professores[cache_key] = professores
            CacheHelper._cache_timestamp[cache_key] = datetime.now()
            logger.info(f"Cache SET: {len(professores)} professores")
            
            return professores
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar professores: {e}")
            return []
    
    @staticmethod
    def get_lista_coordenadores() -> list:
        """Busca lista de coordenadores com cache"""
        cache_key = "coordenadores"
        timestamp = CacheHelper._cache_timestamp.get(cache_key)
        
        if cache_key in CacheHelper._cache_coordenadores:
            if timestamp and datetime.now() - timestamp < timedelta(seconds=CacheHelper.CACHE_TTL):
                logger.info("Cache HIT: lista de coordenadores")
                return CacheHelper._cache_coordenadores[cache_key]
        
        try:
            logger.info("Cache MISS: buscando lista de coordenadores na API")
            response = requests.get(f"{API_URL}/coordenador/get_list_coordenador/", timeout=10)
            response.raise_for_status()
            coordenadores = response.json()
            
            CacheHelper._cache_coordenadores[cache_key] = coordenadores
            CacheHelper._cache_timestamp[cache_key] = datetime.now()
            logger.info(f"Cache SET: {len(coordenadores)} coordenadores")
            
            return coordenadores
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar coordenadores: {e}")
            return []
    
    @staticmethod
    def clear_cache():
        """Limpa o cache (útil para testes ou atualizações)"""
        CacheHelper._cache_disciplinas.clear()
        CacheHelper._cache_professores.clear()
        CacheHelper._cache_coordenadores.clear()
        CacheHelper._cache_timestamp.clear()
        logger.info("Cache limpo")

# ===================================================================
# ERROR HANDLER
# ===================================================================
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
        logger.error(f"API_ERROR: {json.dumps(log_entry, ensure_ascii=False)}")
        
        # Mensagens específicas por tipo de erro
        if isinstance(error, requests.exceptions.Timeout):
            dispatcher.utter_message(
                text="O servidor esta demorando para responder. Por favor, tente novamente em alguns instantes."
            )
        elif isinstance(error, requests.exceptions.ConnectionError):
            dispatcher.utter_message(
                text="Nao foi possivel conectar ao servidor. Verifique sua conexao ou tente mais tarde."
            )
        elif isinstance(error, requests.exceptions.HTTPError):
            if hasattr(error, 'response') and error.response:
                status_code = error.response.status_code
                if status_code == 404:
                    dispatcher.utter_message(
                        text="A informacao solicitada nao foi encontrada no sistema."
                    )
                elif status_code == 500:
                    dispatcher.utter_message(
                        text="Ocorreu um erro interno. Nossa equipe foi notificada. Tente novamente mais tarde."
                    )
                elif status_code == 503:
                    dispatcher.utter_message(
                        text="O servico esta temporariamente indisponivel. Tente novamente em alguns minutos."
                    )
                else:
                    dispatcher.utter_message(
                        text=f"Ocorreu um erro ao processar sua solicitacao (codigo {status_code}). Tente novamente."
                    )
            else:
                dispatcher.utter_message(
                    text="Ocorreu um erro ao processar sua solicitacao. Tente novamente."
                )
        elif isinstance(error, requests.exceptions.JSONDecodeError):
            dispatcher.utter_message(
                text="O servidor retornou uma resposta invalida. Tente novamente mais tarde."
            )
        else:
            dispatcher.utter_message(
                text="Desculpe, ocorreu um erro inesperado. Por favor, tente novamente."
            )

# ===================================================================
# RESPONSE VALIDATOR
# ===================================================================
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
            logger.error(f"Resposta da API nao e JSON valido: {e}")
            return None
    
    @staticmethod
    def validate_list_response(response: requests.Response) -> List:
        """Valida se a resposta é uma lista válida"""
        try:
            data = response.json()
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'value' in data:
                # Algumas APIs retornam {"value": [...]}
                return data['value']
            else:
                logger.warning(f"Resposta nao e uma lista: {type(data)}")
                return []
        except json.JSONDecodeError as e:
            logger.error(f"Resposta da API nao e JSON valido: {e}")
            return []

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
        "comunicado": "Aviso",
        "disciplina": "Disciplina",
        "matéria": "Disciplina",
        "aula": "Disciplina"
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

def get_disciplina_id_by_name(disciplina_nome: Text) -> str | None:
    """
    Busca ID de disciplina usando cache.
    NOTA: Usa endpoint de cronograma que aceita nome (solução temporária).
    """
    return CacheHelper.get_disciplina_id(disciplina_nome)

class ActionBuscarUltimosAvisos(Action):
    def name(self) -> Text:
        return "action_buscar_ultimos_avisos"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pergunta_aluno = tracker.latest_message.get('text')
        # Salvar pergunta do aluno
        salvar_pergunta_aluno(pergunta_aluno)
        
        logger.info(f"[{self.name()}] Buscando avisos")
        dispatcher.utter_message(text="Consultando mural de avisos...")
        
        try:
            response = requests.get(f"{API_URL}/aviso/get_lista_aviso/", timeout=10)
            response.raise_for_status()
            
            # VALIDAÇÃO ADICIONADA
            avisos = ResponseValidator.validate_list_response(response)
            
            if not avisos:
                dispatcher.utter_message(text="Nao ha avisos recentes.")
                logger.info(f"[{self.name()}] Nenhum aviso encontrado")
            else:
                mensagem = "Ultimos Avisos:\n\n"
                for aviso in avisos[:3]:
                    if isinstance(aviso, dict):
                    titulo = aviso.get('titulo', 'Aviso')
                    conteudo = aviso.get('conteudo', '')
                    mensagem += f"Titulo: {titulo}\nConteudo: {conteudo}\n----------------\n"
                dispatcher.utter_message(text=mensagem)
                logger.info(f"[{self.name()}] {len(avisos[:3])} avisos retornados")
        except Exception as e:
            ErrorHandler.handle_api_error(
                dispatcher, e,
                context="Buscar avisos",
                action_name=self.name()
            )
        return []

class ActionBuscarCronograma(Action):
    def name(self) -> Text:
        return "action_buscar_cronograma"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pergunta_aluno = tracker.latest_message.get('text')
        # Salvar pergunta do aluno
        salvar_pergunta_aluno(pergunta_aluno)
        
        disciplina_nome = next(tracker.get_latest_entity_values("disciplina"), None)
        
        if not disciplina_nome:
            dispatcher.utter_message(text="De qual disciplina voce quer saber o horario?")
            return []

        logger.info(f"[{self.name()}] Buscando cronograma para disciplina: {disciplina_nome}")
        disciplina_id = get_disciplina_id_by_name(disciplina_nome)
        
        if not disciplina_id:
            dispatcher.utter_message(text=f"Nao encontrei a disciplina {disciplina_nome}.")
            logger.warning(f"[{self.name()}] Disciplina '{disciplina_nome}' nao encontrada")
            return []

        try:
            response = requests.get(f"{API_URL}/cronograma/disciplina/{disciplina_id}", timeout=10)
            response.raise_for_status()
            
            # VALIDAÇÃO ADICIONADA
            cronogramas = ResponseValidator.validate_list_response(response)
            
            if not cronogramas:
                dispatcher.utter_message(text=f"Sem horarios cadastrados para {disciplina_nome}.")
                logger.info(f"[{self.name()}] Nenhum cronograma encontrado para '{disciplina_nome}'")
            else:
                msg = f"Horario de {disciplina_nome}:\n"
                    for item in cronogramas:
                    if isinstance(item, dict):
                        dia = item.get('dia_semana', '')
                        inicio = item.get('hora_inicio', '')
                        sala = item.get('sala', 'N/A')
                        msg += f"- {dia} as {inicio} (Sala {sala})\n"
                else:
                        logger.warning(f"[{self.name()}] Item do cronograma nao e dict: {type(item)}")
                
                dispatcher.utter_message(text=msg)
                logger.info(f"[{self.name()}] {len(cronogramas)} cronograma(s) retornado(s)")

        except Exception as e:
            ErrorHandler.handle_api_error(
                dispatcher, e,
                context=f"Buscar cronograma - disciplina {disciplina_nome}",
                action_name=self.name()
            )
        return []

#
# ... (mantenha todas as outras classes de actions iguais) ...
#

class ActionGerarRespostaComIA(Action):
    def name(self) -> Text:
        return "action_gerar_resposta_com_ia"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pergunta_aluno = tracker.latest_message.get('text')
        
        # Salvar pergunta do aluno
        salvar_pergunta_aluno(pergunta_aluno)
        
        dispatcher.utter_message(text="Consultando Base de Dados...")

        try:
            # --- ESTA É A CORREÇÃO ---
            # Agora enviamos APENAS o campo "pergunta", exatamente
            # como a sua nova API (ia_services.py) espera.
            payload = {
                "pergunta": pergunta_aluno
            }
            # ---------------------------

            logger.info(f"[{self.name()}] Gerando resposta da IA para: {pergunta_aluno[:50]}...")
            response = requests.post(f"{API_URL}/ia/gerar-resposta", json=payload, timeout=30)
            response.raise_for_status()
            
            # VALIDAÇÃO ADICIONADA
            dados = ResponseValidator.validate_json_response(response, expected_keys=["resposta"])
            
            if not dados:
                dispatcher.utter_message(text="A IA processou mas nao retornou uma resposta valida.")
                logger.warning(f"[{self.name()}] Resposta invalida da IA")
                return []
            
            texto_resposta = dados.get("resposta", "A IA processou mas nao retornou texto.")
            
            # NOVO: Buscar URLs dos documentos usados como referência
            try:
                response_docs = requests.get(
                    f"{API_URL}/ia/testar-baseconhecimento",
                    params={"q": pergunta_aluno},
                    timeout=10
                )
                if response_docs.ok:
                    dados_docs = ResponseValidator.validate_json_response(response_docs)
                    if dados_docs:
                        urls_documentos = dados_docs.get("urls_documentos", [])
                        
                        if urls_documentos:
                            texto_resposta += "\n\n📎 **Documentos de referência:**\n"
                            for i, url in enumerate(urls_documentos[:3], 1):  # Limita a 3
                                texto_resposta += f"{i}. {url}\n"
                            logger.info(f"[{self.name()}] {len(urls_documentos[:3])} URL(s) de referencia adicionada(s)")
            except Exception as e:
                logger.warning(f"[{self.name()}] Erro ao buscar URLs de referencia: {e}")
                # Se falhar, não interrompe a resposta principal
            
            dispatcher.utter_message(text=texto_resposta)
            logger.info(f"[{self.name()}] Resposta da IA gerada com sucesso")

        except Exception as e:
            ErrorHandler.handle_api_error(
                dispatcher, e,
                context=f"Gerar resposta IA - pergunta: {pergunta_aluno[:50]}...",
                action_name=self.name()
            ) 
            
        return []

class ActionBuscarDataAvaliacao(Action):
    def name(self) -> Text:
        return "action_buscar_data_avaliacao"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pergunta_aluno = tracker.latest_message.get('text')
        # Salvar pergunta do aluno
        salvar_pergunta_aluno(pergunta_aluno)
        
        disciplina_nome = next(tracker.get_latest_entity_values("disciplina"), None)
        termo_busca = next(tracker.get_latest_entity_values("tipo_avaliacao"), "prova")

        if not disciplina_nome:
            dispatcher.utter_message(text="Qual a disciplina?")
            return []

        id_disciplina = get_disciplina_id_by_name(disciplina_nome)
        if not id_disciplina:
             dispatcher.utter_message(text=f"Disciplina '{disciplina_nome}' nao encontrada. Verifique se o nome esta correto.")
             return []

        logger.info(f"[{self.name()}] Buscando avaliacoes para disciplina: {disciplina_nome}, tipo: {termo_busca}")
        
        try:
            response = requests.get(f"{API_URL}/avaliacao/disciplina/{id_disciplina}", timeout=10)
            response.raise_for_status()
            
            # VALIDAÇÃO ADICIONADA
            avaliacoes = ResponseValidator.validate_list_response(response)
            
                encontradas = []
            termo_busca_lower = termo_busca.lower()
            
                for aval in avaliacoes:
                if not isinstance(aval, dict):
                    logger.warning(f"[{self.name()}] Item de avaliacao nao e dict: {type(aval)}")
                    continue
                    
                nome_aval = aval.get('topico', '')
                data_aval = aval.get('data', '')
                
                # Pular se topico ou data forem None
                if not nome_aval or not data_aval:
                    continue
                
                nome_aval_lower = nome_aval.lower()
                
                # Melhorar filtro de busca
                if termo_busca_lower == "prova":
                    # Se busca genérica "prova", retorna todas
                    data_fmt = data_aval.split('T')[0] if 'T' in data_aval else data_aval
                    encontradas.append(f"- {nome_aval}: {data_fmt}")
                elif termo_busca_lower in nome_aval_lower:
                    # Se termo específico está no nome
                    data_fmt = data_aval.split('T')[0] if 'T' in data_aval else data_aval
                    encontradas.append(f"- {nome_aval}: {data_fmt}")

                if encontradas:
                    dispatcher.utter_message(text=f"Datas:\n" + "\n".join(encontradas))
                logger.info(f"[{self.name()}] {len(encontradas)} avaliacao(oes) encontrada(s)")
                else:
                    dispatcher.utter_message(text=f"Nao achei datas de {termo_busca} para essa materia.")
                logger.info(f"[{self.name()}] Nenhuma avaliacao encontrada para '{termo_busca}'")
                
        except Exception as e:
            ErrorHandler.handle_api_error(
                dispatcher, e,
                context=f"Buscar avaliacoes - disciplina {disciplina_nome}, tipo {termo_busca}",
                action_name=self.name()
            )
        return []

class ActionBuscarInfoAtividadeAcademica(Action):
    def name(self) -> Text:
        return "action_buscar_info_atividade_academica"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pergunta_aluno = tracker.latest_message.get('text')
        # Salvar pergunta do aluno
        salvar_pergunta_aluno(pergunta_aluno)
        
        atividade = next(tracker.get_latest_entity_values("atividade_academica"), None)
        intent = tracker.latest_message['intent'].get('name')
        
        if not atividade:
            if "tcc" in intent: atividade = "TCC"
            elif "aps" in intent: atividade = "APS"
            elif "estagio" in intent: atividade = "Estagio"
            elif "horas_complementares" in intent: atividade = "Horas Complementares"
        
        if not atividade:
            dispatcher.utter_message(text="Sobre qual atividade voce quer saber? (TCC, APS, Estagio)")
            return []

        logger.info(f"[{self.name()}] Buscando informacoes sobre atividade: {atividade}")
        dispatcher.utter_message(text=f"Buscando informacoes sobre {atividade}...")
        
        try:
            response = requests.get(f"{API_URL}/baseconhecimento/get_buscar", params={"q": atividade}, timeout=10)
            response.raise_for_status()
            
            # VALIDAÇÃO ADICIONADA
            dados = ResponseValidator.validate_json_response(response, expected_keys=["contextos"])
            
            if dados:
                contextos = dados.get("contextos", [])
                
                if contextos and isinstance(contextos, list) and len(contextos) > 0:
                    # Pega o primeiro contexto (resumo)
                    dispatcher.utter_message(text=f"Sobre {atividade}:\n{contextos[0]}")
                    logger.info(f"[{self.name()}] Informacoes encontradas para '{atividade}'")
                else:
                    dispatcher.utter_message(text=f"Nao encontrei informacoes detalhadas sobre {atividade}.")
                    logger.info(f"[{self.name()}] Nenhuma informacao encontrada para '{atividade}'")
            else:
            dispatcher.utter_message(text="Erro ao buscar informacoes do curso.")
                logger.warning(f"[{self.name()}] Resposta invalida da API para '{atividade}'")
                
        except Exception as e:
            ErrorHandler.handle_api_error(
                dispatcher, e,
                context=f"Buscar informacoes sobre atividade - {atividade}",
                action_name=self.name()
            )
        return []

class ActionBuscarAtendimentoDocente(Action):
    def name(self) -> Text:
        return "action_buscar_atendimento_docente"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pergunta_aluno = tracker.latest_message.get('text')
        # Salvar pergunta do aluno
        salvar_pergunta_aluno(pergunta_aluno)
        
        # O formulário garante que o slot 'nome_docente' esta preenchido
        nome_docente = tracker.get_slot("nome_docente")
        
        if not nome_docente:
             # Isso nao deve acontecer se o form estiver certo, mas e uma seguranca
            dispatcher.utter_message(text="De qual professor voce quer o horario?")
            return []

        logger.info(f"[{self.name()}] Buscando atendimento do docente: {nome_docente}")
        
        try:
            # USAR CACHE
            todos = []
            professores = CacheHelper.get_lista_professores()
            coordenadores = CacheHelper.get_lista_coordenadores()
            todos.extend(professores)
            todos.extend(coordenadores)
            
            nome_docente_lower = nome_docente.lower().strip()
            
            for doc in todos:
                if not isinstance(doc, dict):
                    logger.warning(f"[{self.name()}] Item de docente nao e dict: {type(doc)}")
                    continue
                    
                nome = doc.get('nome_professor') or doc.get('nome_coordenador')
                if nome:
                    nome_lower = nome.lower().strip()
                    # Busca mais flexível
                    if nome_docente_lower in nome_lower or nome_lower in nome_docente_lower:
                        horario = doc.get('horario_atendimento', 'Horario nao informado no cadastro.')
                        nome_completo = doc.get('nome_professor') or doc.get('nome_coordenador')
                        dispatcher.utter_message(text=f"Atendimento {nome_completo}:\n{horario}")
                        logger.info(f"[{self.name()}] Atendimento encontrado para '{nome_completo}'")
                        return [SlotSet("nome_docente", None)] # Limpa o slot
                    # Verifica palavras individuais
                    nome_parts = nome_lower.split()
                    if any(part == nome_docente_lower or nome_docente_lower in part for part in nome_parts):
                        horario = doc.get('horario_atendimento', 'Horario nao informado no cadastro.')
                        nome_completo = doc.get('nome_professor') or doc.get('nome_coordenador')
                        dispatcher.utter_message(text=f"Atendimento {nome_completo}:\n{horario}")
                        logger.info(f"[{self.name()}] Atendimento encontrado para '{nome_completo}'")
                        return [SlotSet("nome_docente", None)] # Limpa o slot
            
            dispatcher.utter_message(text=f"Professor(a) {nome_docente} nao encontrado(a).")
            logger.warning(f"[{self.name()}] Docente '{nome_docente}' nao encontrado")

        except Exception as e:
            ErrorHandler.handle_api_error(
                dispatcher, e,
                context=f"Buscar atendimento docente - {nome_docente}",
                action_name=self.name()
            )
            
        return [SlotSet("nome_docente", None)] # Limpa o slot

class ActionBuscarMaterial(Action):
    def name(self) -> Text:
        return "action_buscar_material"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pergunta_aluno = tracker.latest_message.get('text')
        # Salvar pergunta do aluno
        salvar_pergunta_aluno(pergunta_aluno)
        
        # O formulario garante que o slot 'disciplina' esta preenchido
        disciplina_nome = tracker.get_slot("disciplina")
        
        if not disciplina_nome:
            # Isso nao deve acontecer se o form estiver certo
            dispatcher.utter_message(text="Claro. De qual disciplina voce quer o material?")
            return []
        
        logger.info(f"[{self.name()}] Buscando materiais para disciplina: {disciplina_nome}")
        dispatcher.utter_message(text=f"Buscando materiais para {disciplina_nome}...")

        try:
            # SOLUÇÃO: Usar endpoint de teste que retorna documentos com URLs
            response = requests.get(
                f"{API_URL}/ia/testar-baseconhecimento",
                params={"q": disciplina_nome},
                timeout=10
            )
            response.raise_for_status()
            
            # VALIDAÇÃO ADICIONADA
            dados = ResponseValidator.validate_json_response(response)

            if not dados:
                logger.warning(f"[{self.name()}] Resposta invalida da API para '{disciplina_nome}'")
                dispatcher.utter_message(text="Erro ao buscar documentos.")
                return [SlotSet("disciplina", None)]

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
                            text=f"Encontrei informacoes sobre {disciplina_nome}, mas os documentos nao estao disponiveis para download direto. "
                                 f"Consulte o painel administrativo para acessar os arquivos."
                        )
                    else:
                        dispatcher.utter_message(text=f"Nao encontrei materiais para {disciplina_nome} no sistema.")
                else:
                    dispatcher.utter_message(text=f"Nao encontrei materiais para {disciplina_nome} no sistema.")
                    logger.info(f"[{self.name()}] Nenhum material encontrado para '{disciplina_nome}'")

        except Exception as e:
            ErrorHandler.handle_api_error(
                dispatcher, e,
                context=f"Buscar materiais - disciplina {disciplina_nome}",
                action_name=self.name()
            )
        
        # Limpa o slot para a proxima pergunta
        return [SlotSet("disciplina", None)]
    
class ActionBuscarInfoDocente(Action):
    def name(self) -> Text:
        return "action_buscar_info_docente"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pergunta_aluno = tracker.latest_message.get('text')
        # Salvar pergunta do aluno
        salvar_pergunta_aluno(pergunta_aluno)
        
        nome_docente = next(tracker.get_latest_entity_values("nome_docente"), None)
        
        if not nome_docente:
            dispatcher.utter_message(text="Qual o nome do professor?")
            return []

        logger.info(f"[{self.name()}] Buscando informacoes do docente: {nome_docente}")

        try:
            # USAR CACHE
            todos = []
            professores = CacheHelper.get_lista_professores()
            coordenadores = CacheHelper.get_lista_coordenadores()
            todos.extend(professores)
            todos.extend(coordenadores)

            encontrado = None
            nome_docente_lower = nome_docente.lower().strip()
            
            for doc in todos:
                nome = doc.get('nome_professor') or doc.get('nome_coordenador')
                if nome:
                    nome_lower = nome.lower().strip()
                    # Busca mais flexível: verifica se o nome fornecido está no nome completo
                    # ou se o nome completo está no nome fornecido (para apelidos)
                    if nome_docente_lower in nome_lower or nome_lower in nome_docente_lower:
                        encontrado = doc
                        break
                    # Também verifica palavras individuais (ex: "Alvaro" em "Álvaro Prado")
                    nome_parts = nome_lower.split()
                    if any(part == nome_docente_lower or nome_docente_lower in part for part in nome_parts):
                    encontrado = doc
                    break
            
            if encontrado:
                email = encontrado.get('email_institucional', 'Nao informado')
                nome_completo = encontrado.get('nome_professor') or encontrado.get('nome_coordenador')
                dispatcher.utter_message(text=f"Contato Docente\nNome: {nome_completo}\nEmail: {email}")
            else:
                dispatcher.utter_message(text=f"Nao encontrei o professor(a) {nome_docente} no cadastro.")
                logger.warning(f"[{self.name()}] Docente '{nome_docente}' nao encontrado")

        except Exception as e:
            ErrorHandler.handle_api_error(
                dispatcher, e,
                context=f"Buscar informacoes docente - {nome_docente}",
                action_name=self.name()
            )
        return []

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
            
            response_msg.raise_for_status()
            
            # VALIDAÇÃO ADICIONADA
            mensagens = ResponseValidator.validate_list_response(response_msg)
            
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
            logger.info(f"[{self.name()}] Duvidas frequentes retornadas: {len(duvidas_inst)} institucionais, {len(palavras_chave_frequentes)} conteudo")
            
        except Exception as e:
            ErrorHandler.handle_api_error(
                dispatcher, e,
                context="Buscar duvidas frequentes",
                action_name=self.name()
            )
        
        return []