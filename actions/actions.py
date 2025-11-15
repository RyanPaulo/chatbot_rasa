# =================================================================
# CÓDIGO ORIGINAL DO SEU COLEGA (NÃO MEXIDO)
# =================================================================
import platform
import asyncio
from typing import Any, Text, Dict, List
from datetime import datetime
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# PARA FAZER A PONTE ENTRE A NOSSA API FASTAPI
API_URL = "http://127.0.0.1:8000"

class ActionBuscarUltimosAvisos(Action):
    # ... (O CÓDIGO DELE VEM AQUI, EXATAMENTE COMO ESTAVA) ...
    def name(self) -> Text:
        return "action_buscar_ultimos_avisos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Ok, estou buscando os últimos avisos para você...")
        try:
            response = requests.get(f"{API_URL}/aviso/get_lista_aviso/")
            response.raise_for_status() 
            avisos = response.json()
            if not avisos:
                mensagem_final = "Não encontrei nenhum aviso recente."
            else:
                mensagem_final = "Encontrei os seguintes avisos:\n"
                for aviso in avisos[:3]: 
                    mensagem_final += f"- Título: {aviso.get('titulo', 'Sem Título')}\n  Conteúdo: {aviso.get('conteudo', 'Sem Conteúdo')}\n\n"
            dispatcher.utter_message(text=mensagem_final)
        except requests.exceptions.RequestException as e:
            print(f"Erro ao conectar com a API: {e}")
            dispatcher.utter_message(
                text="Desculpe, não consegui me conectar ao sistema de avisos agora. Tente novamente mais tarde.")
        return []

# =================================================================
# FUNÇÃO AUXILIAR (Helper)
# Vamos usar esta função em várias ações para pegar o ID da disciplina
# API Endpoint: GET /disciplinas/get_diciplina_id/{disciplina}
# =================================================================
def get_disciplina_id_by_name(disciplina_nome: Text) -> str | None:
    try:
        # A API diz: /disciplinas/get_diciplina_id/{disciplina}
        response = requests.get(f"{API_URL}/disciplinas/get_diciplina_id/{disciplina_nome}")
        response.raise_for_status()
        return response.json().get("id_disciplina")
    except requests.exceptions.RequestException:
        return None

# =================================================================
# AÇÃO 2: BUSCAR CRONOGRAMA (CÓDIGO CORRIGIDO PARA A API)
# API Endpoint: GET /cronograma/disciplina/{disciplina_id}
# =================================================================
class ActionBuscarCronograma(Action):
    def name(self) -> Text:
        return "action_buscar_cronograma"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disciplina_nome = next(tracker.get_latest_entity_values("disciplina"), None)
        if not disciplina_nome:
            dispatcher.utter_message(text="Para qual disciplina você gostaria de ver o cronograma?")
            return []
        dispatcher.utter_message(text=f"Ok, buscando o cronograma para '{disciplina_nome}'...")
        disciplina_id = get_disciplina_id_by_name(disciplina_nome)
        if not disciplina_id:
            dispatcher.utter_message(text=f"Não consegui encontrar a disciplina '{disciplina_nome}'. Verifique se o nome está correto.")
            return []
        try:
            cronograma_response = requests.get(f"{API_URL}/cronograma/disciplina/{disciplina_id}")
            cronograma_response.raise_for_status()
            cronogramas = cronograma_response.json()
            if not cronogramas:
                mensagem_final = f"Não encontrei um cronograma para a disciplina '{disciplina_nome}'."
            else:
                mensagem_final = f"Aqui está o cronograma para '{disciplina_nome}':\n"
                for item in cronogramas:
                    dia = item.get('dia_semana', 'Dia não informado')
                    hora_inicio_str = item.get('hora_inicio', '')
                    hora_fim_str = item.get('hora_fim', '')
                    try:
                        hora_inicio_fmt = datetime.strptime(hora_inicio_str, '%H:%M:%S').strftime('%H:%M') if hora_inicio_str else ''
                        hora_fim_fmt = datetime.strptime(hora_fim_str, '%H:%M:%S').strftime('%H:%M') if hora_fim_str else ''
                        mensagem_final += f"- {dia}: das {hora_inicio_fmt} às {hora_fim_fmt}\n"
                    except ValueError:
                         mensagem_final += f"- {dia}: {hora_inicio_str} às {hora_fim_str}\n"
            dispatcher.utter_message(text=mensagem_final)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                dispatcher.utter_message(text=f"Não encontrei cronograma para '{disciplina_nome}'.")
            else:
                dispatcher.utter_message(text="Ocorreu um erro ao buscar o cronograma. Tente novamente.")
        except requests.exceptions.RequestException:
            dispatcher.utter_message(text="Desculpe, não consegui acessar o sistema de cronogramas agora.")
        return []

# =================================================================
# == AQUI COMEÇAM AS NOVAS AÇÕES (AGORA MAIS SIMPLES!) ==
# =================================================================

# --- Ação de "Fallback" para o Gemini ---
# Esta ação única vai lidar com TODAS as perguntas de conteúdo
# Ela vai chamar o endpoint do seu colega: POST /ia/gerar-resposta
class ActionGerarRespostaComIA(Action):
    
    def name(self) -> Text:
        # Este é um nome genérico. Vamos usá-lo para várias intenções.
        return "action_gerar_resposta_com_ia"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # 1. Pegar a pergunta EXATA do aluno
        pergunta_aluno = tracker.latest_message.get('text')
        dispatcher.utter_message(text="Ok, estou consultando nossos materiais para te dar uma resposta...")

        try:
            # 2. Chamar o endpoint da SUA API (o "Gemini Embutido")
            # API: POST /ia/gerar-resposta
            # A API dele espera um JSON com "pergunta" e "descricao"
            # Vamos mandar a pergunta do aluno nos dois campos
            payload = {
                "pergunta": pergunta_aluno,
                "descricao": pergunta_aluno 
            }
            response = requests.post(f"{API_URL}/ia/gerar-resposta", json=payload)
            response.raise_for_status()
            
            # 3. Pegar a resposta da API e enviar ao usuário
            resposta_api = response.json() 
            
            # (Não sei o formato da resposta, vou chutar que é {"resposta": "..."})
            mensagem_final = resposta_api.get("resposta", "Não consegui formular uma resposta com base nos materiais.")
            
            dispatcher.utter_message(text=mensagem_final)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                dispatcher.utter_message(text="Não encontrei nenhuma informação sobre isso nos materiais cadastrados.")
            else:
                dispatcher.utter_message(text="Desculpe, tive um problema ao consultar o sistema de IA.")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao conectar com a API de IA: {e}")
            dispatcher.utter_message(text="Desculpe, não consegui me conectar ao sistema de inteligência artificial agora.")
        
        return []

# --- Ação para UC07: Dúvidas Acadêmicas (Datas de Provas/Prazos) ---
# (Esta ação NÃO usa o Gemini, ela busca dados estruturados)
class ActionBuscarDataAvaliacao(Action):
    def name(self) -> Text:
        return "action_buscar_data_avaliacao"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disciplina_nome = next(tracker.get_latest_entity_values("disciplina"), None)
        termo_busca = next(tracker.get_latest_entity_values("tipo_avaliacao"), None) or \
                      next(tracker.get_latest_entity_values("prazo_tipo"), None)

        if not termo_busca:
            dispatcher.utter_message(text="Qual prazo ou prova você quer saber a data? (Ex: NP1, APS, TCC...)")
            return []
        if not disciplina_nome:
            dispatcher.utter_message(text=f"Certo. E para qual disciplina é o prazo de '{termo_busca}'?")
            return []
        dispatcher.utter_message(text=f"Buscando a data de '{termo_busca}' para '{disciplina_nome}'...")

        disciplina_id = get_disciplina_id_by_name(disciplina_nome)
        if not disciplina_id:
            dispatcher.utter_message(text=f"Não consegui encontrar a disciplina '{disciplina_nome}'. Verifique se o nome está correto.")
            return []
        try:
            response = requests.get(f"{API_URL}/avaliacao/disciplina/{disciplina_id}")
            response.raise_for_status()
            avaliacoes = response.json()
            if not avaliacoes:
                mensagem_final = f"Ainda não há avaliações cadastradas para '{disciplina_nome}'."
            else:
                resultados = []
                for aval in avaliacoes:
                    if aval.get('tipo_avaliacao', '').lower() == termo_busca.lower():
                        resultados.append(aval)
                if not resultados:
                    mensagem_final = f"Não encontrei a data para '{termo_busca}' de '{disciplina_nome}'."
                else:
                    mensagem_final = f"Encontrei estas datas para '{termo_busca}' de '{disciplina_nome}':\n"
                    for item in resultados:
                        data_fmt = datetime.fromisoformat(item['data']).strftime('%d/%m/%Y')
                        mensagem_final += f"- {item.get('tipo_avaliacao', termo_busca)}: {data_fmt}\n"
            dispatcher.utter_message(text=mensagem_final)
        except requests.exceptions.RequestException:
            dispatcher.utter_message(text="Desculpe, não consegui acessar o calendário agora.")
        return []

# --- AÇÃO 7: BUSCAR INFO DOCENTE (NÃO USA GEMINI) ---
class ActionBuscarInfoDocente(Action):
    def name(self) -> Text:
        return "action_buscar_info_docente"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nome_docente = next(tracker.get_latest_entity_values("nome_docente"), None)
        info_desejada = next(tracker.get_latest_entity_values("info_docente"), "todas")

        if not nome_docente:
            dispatcher.utter_message(text="Sobre qual professor ou professora você quer informações?")
            return []
        dispatcher.utter_message(text=f"Buscando informações sobre '{nome_docente}'...")
        
        try:
            prof_res = requests.get(f"{API_URL}/professores/lista_professores/")
            coord_res = requests.get(f"{API_URL}/coordenador/get_list_coordenador/")
            todos_docentes = (prof_res.json() if prof_res.ok else []) + (coord_res.json() if coord_res.ok else [])

            if not todos_docentes:
                dispatcher.utter_message(text="Não consegui carregar a lista de docentes do sistema.")
                return []

            docente_encontrado = None
            for docente in todos_docentes:
                nome_api = docente.get('nome_professor') or docente.get('nome_coordenador')
                if nome_api and nome_api.lower() == nome_docente.lower():
                    docente_encontrado = docente
                    break
            
            if not docente_encontrado:
                mensagem_final = f"Não encontrei informações para '{nome_docente}'."
            else:
                email = docente_encontrado.get('email_institucional')
                sala = docente_encontrado.get('sala', 'Não informada') # Chutei "sala"
                atendimento = docente_encontrado.get('horario_atendimento', 'Não informado') # Chutei "horario_atendimento"

                if info_desejada in ("email", "e-mail"):
                    mensagem_final = f"O email de '{nome_docente}' é: {email}"
                elif info_desejada == "sala":
                    mensagem_final = f"A sala de '{nome_docente}' é: {sala}"
                elif info_desejada in ("horário de atendimento", "contato", "horário"):
                     mensagem_final = f"O horário de atendimento de '{nome_docente}' é: {atendimento}"
                else:
                    mensagem_final = f"Informações de '{nome_docente}':\n- Email: {email}\n- Sala: {sala}\n- Atendimento: {atendimento}"
            
            dispatcher.utter_message(text=mensagem_final)

        except requests.exceptions.RequestException:
            dispatcher.utter_message(text="Desculpe, não consegui acessar o sistema de docentes agora.")
        return []

# --- AÇÃO 8: BUSCAR INFO ATIVIDADE (NÃO USA GEMINI) ---
class ActionBuscarInfoAtividadeAcademica(Action):
    def name(self) -> Text:
        return "action_buscar_info_atividade_academica"
    # ... (O código desta ação que te mandei antes estava correto, 
    # buscando na "baseconhecimento". Pode mantê-lo aqui.) ...
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        atividade = next(tracker.get_latest_entity_values("atividade_academica"), None)
        if not atividade:
            dispatcher.utter_message(text="Sobre qual atividade acadêmica você quer informações (TCC, APS, Estágio...)?")
            return []
        dispatcher.utter_message(text=f"Buscando informações sobre '{atividade}'...")
        try:
            response = requests.get(f"{API_URL}/baseconhecimento/get_buscar", params={"q": atividade})
            response.raise_for_status()
            info = response.json()
            if not info:
                mensagem_final = f"Não encontrei informações sobre '{atividade}'."
            else:
                if isinstance(info, list):
                    info = info[0] 
                mensagem_final = f"Informações sobre '{info.get('pergunta_padrao', atividade)}':\n"
                mensagem_final += f"{info.get('resposta', 'Descrição não disponível.')}\n"
            dispatcher.utter_message(text=mensagem_final)
        except requests.exceptions.RequestException:
            dispatcher.utter_message(text="Desculpe, não consegui acessar o sistema de informações acadêmicas agora.")
        return []