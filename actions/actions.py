import platform
import asyncio
from typing import Any, Text, Dict, List
from datetime import datetime
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
from rasa_sdk.events import SlotSet

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

API_URL = "http://127.0.0.1:8000"

def get_disciplina_id_by_name(disciplina_nome: Text) -> str | None:
    try:
        response = requests.get(f"{API_URL}/disciplinas/get_diciplina_id/{disciplina_nome}")
        response.raise_for_status()
        return response.json().get("id_disciplina")
    except requests.exceptions.RequestException:
        return None

class ActionBuscarUltimosAvisos(Action):
    def name(self) -> Text:
        return "action_buscar_ultimos_avisos"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Consultando mural de avisos...")
        try:
            response = requests.get(f"{API_URL}/aviso/get_lista_aviso/")
            response.raise_for_status()
            avisos = response.json()
            
            if not avisos:
                dispatcher.utter_message(text="Nao ha avisos recentes.")
            else:
                mensagem = "Ultimos Avisos:\n\n"
                for aviso in avisos[:3]:
                    titulo = aviso.get('titulo', 'Aviso')
                    conteudo = aviso.get('conteudo', '')
                    mensagem += f"Titulo: {titulo}\nConteudo: {conteudo}\n----------------\n"
                dispatcher.utter_message(text=mensagem)
        except Exception as e:
            print(f"Erro API: {e}")
            dispatcher.utter_message(text="Erro ao conectar ao sistema de avisos.")
        return []

class ActionBuscarCronograma(Action):
    def name(self) -> Text:
        return "action_buscar_cronograma"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disciplina_nome = next(tracker.get_latest_entity_values("disciplina"), None)
        
        if not disciplina_nome:
            dispatcher.utter_message(text="De qual disciplina voce quer saber o horario?")
            return []

        disciplina_id = get_disciplina_id_by_name(disciplina_nome)
        
        if not disciplina_id:
            dispatcher.utter_message(text=f"Nao encontrei a disciplina {disciplina_nome}.")
            return []

        try:
            response = requests.get(f"{API_URL}/cronograma/disciplina/{disciplina_id}")
            response.raise_for_status()
            cronogramas = response.json()
            
            if not cronogramas:
                dispatcher.utter_message(text=f"Sem horarios cadastrados para {disciplina_nome}.")
            else:
                msg = f"Horario de {disciplina_nome}:\n"
                if isinstance(cronogramas, list):
                    for item in cronogramas:
                        dia = item.get('dia_semana', '')
                        inicio = item.get('hora_inicio', '')
                        sala = item.get('sala', 'N/A')
                        msg += f"- {dia} as {inicio} (Sala {sala})\n"
                else:
                     msg += f"- {cronogramas.get('dia_semana')} as {cronogramas.get('hora_inicio')} (Sala {cronogramas.get('sala')})"
                
                dispatcher.utter_message(text=msg)

        except Exception:
            dispatcher.utter_message(text="Erro ao buscar cronograma.")
        return []

#
# ... (mantenha todas as outras classes de actions iguais) ...
#

class ActionGerarRespostaComIA(Action):
    def name(self) -> Text:
        return "action_gerar_resposta_com_ia"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pergunta_aluno = tracker.latest_message.get('text')
        dispatcher.utter_message(text="Consultando Base de Dados...")

        try:
            # --- ESTA É A CORREÇÃO ---
            # Agora enviamos APENAS o campo "pergunta", exatamente
            # como a sua nova API (ia_services.py) espera.
            payload = {
                "pergunta": pergunta_aluno
            }
            # ---------------------------

            response = requests.post(f"{API_URL}/ia/gerar-resposta", json=payload)
            response.raise_for_status()
            
            dados = response.json()
            texto_resposta = dados.get("resposta", "A IA processou mas nao retornou texto.")
            dispatcher.utter_message(text=texto_resposta)

        except Exception as e:
            print(f"Erro IA: {e}")
            # Esta é a mensagem de erro que você viu no print
            dispatcher.utter_message(text="Erro ao conectar com a IA.") 
            
        return []

class ActionBuscarDataAvaliacao(Action):
    def name(self) -> Text:
        return "action_buscar_data_avaliacao"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disciplina_nome = next(tracker.get_latest_entity_values("disciplina"), None)
        termo_busca = next(tracker.get_latest_entity_values("tipo_avaliacao"), "prova")

        if not disciplina_nome:
            dispatcher.utter_message(text="Qual a disciplina?")
            return []

        id_disciplina = get_disciplina_id_by_name(disciplina_nome)
        if not id_disciplina:
             dispatcher.utter_message(text=f"Disciplina '{disciplina_nome}' nao encontrada. Verifique se o nome esta correto.")
             return []

        try:
            response = requests.get(f"{API_URL}/avaliacao/disciplina/{id_disciplina}")
            if response.ok:
                avaliacoes = response.json()
                encontradas = []
                for aval in avaliacoes:
                    nome_aval = aval.get('topico', '').lower()
                    if termo_busca.lower() in nome_aval or termo_busca == "prova":
                        data_fmt = aval.get('data', '').split('T')[0]
                        encontradas.append(f"- {aval.get('topico')}: {data_fmt}")

                if encontradas:
                    dispatcher.utter_message(text=f"Datas:\n" + "\n".join(encontradas))
                else:
                    dispatcher.utter_message(text=f"Nao achei datas de {termo_busca} para essa materia.")
        except Exception:
            dispatcher.utter_message(text="Erro ao buscar avaliacoes.")
        return []

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
            dispatcher.utter_message(text="Sobre qual atividade voce quer saber? (TCC, APS, Estagio)")
            return []

        dispatcher.utter_message(text=f"Buscando informacoes sobre {atividade}...")
        try:
            response = requests.get(f"{API_URL}/baseconhecimento/get_buscar", params={"q": atividade})
            if response.ok:
                infos = response.json()
                if infos and isinstance(infos, list):
                    info = infos[0]
                    dispatcher.utter_message(text=f"Sobre {atividade}:\n{info.get('resposta', '')}")
                else:
                    dispatcher.utter_message(text=f"Nao encontrei informacoes detalhadas sobre {atividade}.")
        except Exception:
            dispatcher.utter_message(text="Erro ao buscar informacoes do curso.")
        return []

class ActionBuscarAtendimentoDocente(Action):
    def name(self) -> Text:
        return "action_buscar_atendimento_docente"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # O formulário garante que o slot 'nome_docente' esta preenchido
        nome_docente = tracker.get_slot("nome_docente")
        
        if not nome_docente:
             # Isso nao deve acontecer se o form estiver certo, mas e uma seguranca
            dispatcher.utter_message(text="De qual professor voce quer o horario?")
            return []

        try:
            response = requests.get(f"{API_URL}/professores/lista_professores/")
            if response.ok:
                for doc in response.json():
                    if nome_docente.lower() in doc.get('nome_professor', '').lower():
                        horario = doc.get('horario_atendimento', 'Horario nao informado no cadastro.')
                        dispatcher.utter_message(text=f"Atendimento {doc['nome_professor']}:\n{horario}")
                        return [SlotSet("nome_docente", None)] # Limpa o slot
            
            dispatcher.utter_message(text=f"Professor(a) {nome_docente} nao encontrado(a).")

        except Exception:
            dispatcher.utter_message(text="Erro ao buscar lista de docentes.")
            
        return [SlotSet("nome_docente", None)] # Limpa o slot

class ActionBuscarMaterial(Action):
    def name(self) -> Text:
        return "action_buscar_material"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # O formulario garante que o slot 'disciplina' esta preenchido
        disciplina_nome = tracker.get_slot("disciplina")
        
        if not disciplina_nome:
            # Isso nao deve acontecer se o form estiver certo
            dispatcher.utter_message(text="Claro. De qual disciplina voce quer o material?")
            return []
        
        id_disciplina = get_disciplina_id_by_name(disciplina_nome)
        if not id_disciplina:
             # Correcao do bug de string que vimos
             dispatcher.utter_message(text=f"Disciplina '{disciplina_nome}' nao encontrada. Verifique se o nome esta correto.")
             return [SlotSet("disciplina", None)]

        dispatcher.utter_message(text=f"Buscando materiais para {disciplina_nome}...")

        try:
            response = requests.get(f"{API_URL}/documento/disciplina/{id_disciplina}")
            response.raise_for_status()
            documentos = response.json()

            if not documentos:
                dispatcher.utter_message(text=f"Nao encontrei materiais (slides, PDFs) para {disciplina_nome} no sistema.")
                return [SlotSet("disciplina", None)]

            mensagem = f"Encontrei estes materiais para {disciplina_nome}:\n"
            for doc in documentos:
                nome = doc.get("nome_documento", "Material sem nome")
                url = doc.get("url_documento", "")
                mensagem += f"\n- {nome}\n  Link: {url}\n"
            
            dispatcher.utter_message(text=mensagem)

        except Exception as e:
            print(f"Erro ao buscar documentos: {e}")
            dispatcher.utter_message(text="Erro ao conectar ao sistema de documentos.")
        
        # Limpa o slot para a proxima pergunta
        return [SlotSet("disciplina", None)]
    
class ActionBuscarInfoDocente(Action):
    def name(self) -> Text:
        return "action_buscar_info_docente"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nome_docente = next(tracker.get_latest_entity_values("nome_docente"), None)
        
        if not nome_docente:
            dispatcher.utter_message(text="Qual o nome do professor?")
            return []

        try:
            response = requests.get(f"{API_URL}/professores/lista_professores/")
            response_coord = requests.get(f"{API_URL}/coordenador/get_list_coordenador/")
            
            todos = []
            if response.ok: todos.extend(response.json())
            if response_coord.ok: todos.extend(response_coord.json())

            encontrado = None
            for doc in todos:
                nome = doc.get('nome_professor') or doc.get('nome_coordenador')
                if nome and nome_docente.lower() in nome.lower():
                    encontrado = doc
                    break
            
            if encontrado:
                email = encontrado.get('email_institucional', 'Nao informado')
                nome_completo = encontrado.get('nome_professor') or encontrado.get('nome_coordenador')
                dispatcher.utter_message(text=f"Contato Docente\nNome: {nome_completo}\nEmail: {email}")
            else:
                dispatcher.utter_message(text=f"Nao encontrei o professor(a) {nome_docente} no cadastro.")

        except Exception:
            dispatcher.utter_message(text="Erro ao buscar lista de professores.")
        return []