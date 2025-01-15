import sys
import os
from datetime import datetime

# Configuração de logs
log_dir = os.path.join(os.getcwd(), "logsAI")
os.makedirs(log_dir, exist_ok=True)  # Cria o diretório "logs" se não existir
log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")

# Função para redirecionar stdout e stderr
class Logger:
    def __init__(self, log_file):
        self.terminal = sys.stdout  # Saída padrão (console)
        self.log = open(log_file, "a")  # Arquivo de log

    def write(self, message):
        self.terminal.write(message)  # Escreve no console
        self.log.write(message)  # Escreve no arquivo

    def flush(self):
        self.terminal.flush()
        self.log.flush()

# Redireciona stdout e stderr para o arquivo de log
sys.stdout = Logger(log_file)
sys.stderr = Logger(log_file)

# Mensagem inicial no log
print(f"Log iniciado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
print(f"Todos os prints, erros e logs estão sendo gravados em: {log_file}\n")

from fastapi import FastAPI
from router import router
import uvicorn
from utils import *

# Inicializa o FastAPI
app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    # Gerencia arquivos no início
    manage_main_files()

    # Inicializa IA.INI, se necessário
    if not os.path.exists(IA_INI_FILE):
        initialize_ia_file()

    port = find_port_in_range(8000, 8888)
    update_server_port(port)

    # Executa o servidor Uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
        log_config={
            "version": 1,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "file": {
                    "class": "logging.FileHandler",
                    "filename": log_file,
                    "formatter": "default",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["file"],
            },
        },
    )

    # Fecha o arquivo de log ao encerrar
    sys.stdout.log.close()
    sys.stderr.log.close()
