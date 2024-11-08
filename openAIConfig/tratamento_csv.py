import pandas as pd
import numpy as np
import csv
import re
import unicodedata
import logging
from datetime import datetime
import chardet

logging.basicConfig(level=logging.INFO)

def process_csv_for_embeddings(input_csv_path, output_csv_path):
    """
    Processa um arquivo CSV para garantir que esteja adequado para gerar embeddings.

    Parâmetros:
        input_csv_path (str): Caminho para o arquivo CSV de entrada.
        output_csv_path (str): Caminho onde o arquivo CSV processado será salvo.
    """
    logging.info(f"Processando o arquivo CSV: {input_csv_path}")

    # Detectar a codificação do arquivo de entrada
    with open(input_csv_path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']
        logging.info(f"Codificação detectada para {input_csv_path}: {encoding}")

    # Ler o arquivo CSV com a codificação detectada
    try:
        df = pd.read_csv(input_csv_path, encoding=encoding, on_bad_lines='skip')
        logging.info(f"CSV carregado com sucesso. Linhas: {len(df)}")
    except Exception as e:
        logging.error(f"Erro ao ler o arquivo CSV: {str(e)}")
        raise Exception(f"Erro ao ler o arquivo CSV: {str(e)}")

    # Continue com o restante do processamento...
    # (Seu código de limpeza e preparação dos dados)

    # Salvar o CSV processado com a mesma codificação
    try:
        df.to_csv(output_csv_path, index=False, quoting=csv.QUOTE_NONNUMERIC, encoding=encoding)
        logging.info(f"Arquivo CSV processado e salvo em {output_csv_path} com codificação {encoding}")
    except Exception as e:
        logging.error(f"Erro ao salvar o arquivo CSV processado: {str(e)}")
        raise Exception(f"Erro ao salvar o arquivo CSV processado: {str(e)}")

