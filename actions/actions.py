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

# URL da nossa API FastAPI
API_URL = "http://127.0.0.1:8000"

class ActionBuscarUltimosAvisos(Action):

    def name(self) -> Text:
        return "action_buscar_ultimos_avisos"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Mensagem de espera para o usuário
        dispatcher.utter_message(text="Ok, estou buscando os últimos avisos para você...")

        try:
            # Faz a chamada GET para o endpoint /avisos da nossa API
            response = requests.get(f"{API_URL}/aviso/")
            response.raise_for_status()  # Lança um erro se a API retornar erro (4xx ou 5xx)

            avisos = response.json()

            if not avisos:
                mensagem_final = "Não encontrei nenhum aviso recente."
            else:
                # Formata a resposta para o usuário
                mensagem_final = "Encontrei os seguintes avisos:\n"
                for aviso in avisos[:3]:  # Pega os 3 primeiros avisos
                    mensagem_final += f"- Título: {aviso['titulo']}\n  Conteúdo: {aviso['conteudo']}\n\n"

            dispatcher.utter_message(text=mensagem_final)

        except requests.exceptions.RequestException as e:
            print(f"Erro ao conectar com a API: {e}")
            dispatcher.utter_message(
                text="Desculpe, não consegui me conectar ao sistema de avisos agora. Tente novamente mais tarde.")

        return []


# class ActionBuscarCronograma(Action):
#
#     def name(self) -> Text:
#         return "action_buscar_cronograma"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         # Extrair o nome da disciplina que o usuário falou
#         disciplina_nome = next(tracker.get_latest_entity_values("disciplina"), None)
#
#         if not disciplina_nome:
#             dispatcher.utter_message(text="Para qual disciplina você gostaria de ver o cronograma?")
#             return []
#
#         dispatcher.utter_message(text=f"Ok, buscando o cronograma para a disciplina '{disciplina_nome}'...")
#
#         try:
#             # Fazer a chamada para a sua API
#             response = requests.get(f"{API_URL}/disciplina/{disciplina_nome}/cronograma")
#             response.raise_for_status()
#
#             cronogramas = response.json()
#
#             if not cronogramas:
#                 mensagem_final = f"Não encontrei um cronograma para a disciplina '{disciplina_nome}'. Verifique se o nome está correto."
#             else:
#                 # Formatar a resposta para o usuário
#                 mensagem_final = f"Aqui está o cronograma para '{disciplina_nome}':\n"
#                 for item in cronogramas:
#                     dia = item.get('dia_semana', 'Dia não informado')
#                     hora_inicio = item.get('hora_inicio', '')
#                     hora_fim = item.get('hora_fim', '')
#
#                     # Formata as horas para hh:mm
#                     hora_inicio_fmt = datetime.fromisoformat(hora_inicio).strftime('%H:%M') if hora_inicio else ''
#                     hora_fim_fmt = datetime.fromisoformat(hora_fim).strftime('%H:%M') if hora_fim else ''
#
#                     mensagem_final += f"- {dia}: das {hora_inicio_fmt} às {hora_fim_fmt}\n"
#
#             dispatcher.utter_message(text=mensagem_final)
#
#
#         except requests.exceptions.HTTPError as e:
#
#             if e.response.status_code == 404:
#
#                 # A API retornou "Não encontrado"
#
#                 dispatcher.utter_message(
#                     text=f"Não encontrei um cronograma para a disciplina '{disciplina_nome}'. Verifique se o nome está correto.")
#             else:
#
#                 # Outro erro HTTP
#
#                 dispatcher.utter_message(text="Ocorreu um erro ao buscar o cronograma. Tente novamente.")
#
#         except requests.exceptions.RequestException as e:
#
#             # Erro de conexão com a API
#
#             print(f"Erro ao conectar com a API para buscar cronograma: {e}")
#
#             dispatcher.utter_message(
#                 text="Desculpe, não consegui acessar o sistema de cronogramas agora. Tente novamente mais tarde.")
#
#         return []

class ActionBuscarCronograma(Action):
    def name(self) -> Text:
        return "action_buscar_cronograma"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disciplina_nome = next(tracker.get_latest_entity_values("disciplina"), None)
        if not disciplina_nome:
            dispatcher.utter_message(text="Para qual disciplina você gostaria de ver o cronograma?")
            return []

        dispatcher.utter_message(text=f"Ok, buscando o cronograma para '{disciplina_nome}'...")

        try:
            # CORREÇÃO: Primeiro, buscamos a disciplina pelo nome para obter o ID
            disciplina_response = requests.get(f"{API_URL}/disciplina/nome/{disciplina_nome}")
            disciplina_response.raise_for_status()
            disciplina_id = disciplina_response.json().get("id_disciplina")

            if not disciplina_id:
                dispatcher.utter_message(text=f"Não consegui encontrar a disciplina '{disciplina_nome}'.")
                return []

            # AGORA, buscamos o cronograma usando o ID da disciplina
            # Assumindo que seu endpoint de cronograma permite filtrar por id_disciplina
            # Ex: GET /cronograma?id_disciplina=uuid-da-disciplina
            cronograma_response = requests.get(f"{API_URL}/cronograma", params={"id_disciplina": disciplina_id})
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

                    hora_inicio_fmt = datetime.fromisoformat(hora_inicio_str).strftime(
                        '%H:%M') if hora_inicio_str else ''
                    hora_fim_fmt = datetime.fromisoformat(hora_fim_str).strftime('%H:%M') if hora_fim_str else ''

                    mensagem_final += f"- {dia}: das {hora_inicio_fmt} às {hora_fim_fmt}\n"

            dispatcher.utter_message(text=mensagem_final)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                dispatcher.utter_message(
                    text=f"Não encontrei a disciplina ou o cronograma para '{disciplina_nome}'. Verifique o nome.")
            else:
                dispatcher.utter_message(text="Ocorreu um erro ao buscar o cronograma. Tente novamente.")
        except requests.exceptions.RequestException:
            dispatcher.utter_message(text="Desculpe, não consegui acessar o sistema de cronogramas agora.")
        return []