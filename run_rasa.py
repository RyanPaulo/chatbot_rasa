# Arquivo: run_rasa.py

import asyncio
import platform
import sys
from rasa.__main__ import main

# ==============================================================================
#  CORREÇÃO OBRIGATÓRIA PARA ASYNCIO NO WINDOWS
# ==============================================================================
# Aplica a política de evento correta ANTES de qualquer outra coisa.
# Isso força todo o processo do Rasa a usar a política compatível.
if platform.system() == "Windows":
    print("INFO: Aplicando a política de evento do Windows (WindowsSelectorEventLoopPolicy)...")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# ==============================================================================

if __name__ == '__main__':
    # Simula a execução do comando "rasa run" a partir da linha de comando
    # Adicione ou remova argumentos conforme necessário
    sys.argv.extend([
        "run",
        "-m", "models",
        "--enable-api",
        "--cors", "*",
        "--credentials", "credentials.yml"
    ])
    print(f"INFO: Iniciando o servidor Rasa com os argumentos: {sys.argv}")
    main()

