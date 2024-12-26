import configparser
import os

IA_INI_FILE = "ia.ini"

def read_ia_file():
    """
    Lê os valores atuais do arquivo ia.ini.
    """
    if not os.path.exists(IA_INI_FILE):
        initialize_ia_file()

    config = configparser.ConfigParser()
    config.read(IA_INI_FILE)

    # Converte os valores para inteiros ou floats
    ncm = float(config['USAGE']['ncm'])
    ia = float(config['USAGE']['ia'])

    return {'ncm': ncm, 'ia': ia}

def initialize_ia_file():
    """
    Inicializa o arquivo ia.ini com valores iniciais.
    """
    config = configparser.ConfigParser()
    config['USAGE'] = {
        'ncm': '0',
        'ia': '0'
    }
    with open(IA_INI_FILE, 'w') as configfile:
        config.write(configfile)
    print(f"Arquivo {IA_INI_FILE} criado com valores iniciais.")

def update_ncm_usage(ncm_increment):
    """
    Atualiza os valores de ncm no arquivo ia.ini.
    """
    current_usage = read_ia_file()
    new_ncm = current_usage['ncm'] + ncm_increment

    # Atualiza o arquivo
    config = configparser.ConfigParser()
    config['USAGE'] = {
        'ncm': str(new_ncm),
        'ia': str(current_usage['ia'])
    }
    with open(IA_INI_FILE, 'w') as configfile:
        config.write(configfile)

    print(f"NCM atualizado: ncm={new_ncm}")

def update_ia_usage(ia_increment):
    """
    Atualiza os valores de ia no arquivo ia.ini.
    """
    current_usage = read_ia_file()
    new_ia = current_usage['ia'] + ia_increment

    # Atualiza o arquivo
    config = configparser.ConfigParser()
    config['USAGE'] = {
        'ncm': str(current_usage['ncm']),
        'ia': str(new_ia)
    }
    with open(IA_INI_FILE, 'w') as configfile:
        config.write(configfile)

    print(f"IA atualizado: ia={new_ia}")


def update_server_port(port):
    """
    Atualiza a porta do servidor no arquivo ia.ini.
    """
    config = configparser.ConfigParser()
    config.read(IA_INI_FILE)

    # Atualiza a seção SERVER
    config['SERVER'] = {'port': str(port)}

    with open(IA_INI_FILE, 'w') as configfile:
        config.write(configfile)

    print(f"Porta do servidor atualizada para: {port}")

import uvicorn
from fastapi import FastAPI
import random
import socket

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Servidor rodando em porta dinâmica"}

def find_port_in_range(start=8000, end=8888):
    """
    Encontra uma porta livre dentro de um intervalo.
    """
    for _ in range(800):  # Tenta encontrar uma porta em 100 iterações
        port = random.randint(start, end)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))  # Tenta vincular a porta
                return port  # Retorna se for bem-sucedido
            except OSError:
                continue  # Porta já em uso, tenta outra
    raise RuntimeError("Não foi possível encontrar uma porta disponível no intervalo.")

