from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

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