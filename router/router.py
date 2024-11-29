import os
import sys
from http.client import HTTPException

import firebirdsql
from fastapi import FastAPI, APIRouter, Query

from openAIConfig import querycreator
from openAIConfig.embeddings import create_ai_reply, check_ncm_similarity
from openAIConfig.queryCreator import queryNCMcreator, interpret_questionSQLs
import pandas as pd
from utils import *
from pathlib import Path

BASE_DIR = os.getcwd()
bdP = f'{BASE_DIR}/db.fdb'

router = APIRouter()

@router.get('/')
def testserver():
    return {"response": "Servidor testado"}

@router.get("/askai")
def get_askai(userQuestion: str = Query(...)):
    usage = read_ia_file()
    ia_cost = usage['ia']
    if ia_cost < 10:
        try:
            responseSql = clean_sql_response(interpret_questionSQLs(userQuestion))
            print(responseSql)
            response = process_user_question(responseSql, userQuestion)
            return {"response": response}
        except ValueError as ve:
            raise HTTPException(status=400, detail=f"Erro de validação: {str(ve)}")
        except FileNotFoundError as fnf:
            raise HTTPException(status=404, detail=f"Arquivo não encontrado: {str(fnf)}")
        except Exception as e:
            raise HTTPException(status=500, detail=f"Erro no servidor: {str(e)}")
    else:
        return {"response": "limite máximo de pesquisas atingido"}


@router.get("/askai/ncm/")
def get_ncm(product_name: str):
    usage = read_ia_file()
    ncm_cost = usage['ncm']
    if ncm_cost < 50:
        try:
            # Calcular similaridade e obter o contexto relevante
            similarity_df = check_ncm_similarity(product_name)
            top_ncm_data = similarity_df.head(1).to_dict('records')[0]  # Obtém a linha mais relevante

            # Gera a resposta do NCM
            response = queryNCMcreator(data=top_ncm_data, question=product_name)
            return {"ncm": response}
        except Exception as e:
            raise HTTPException(status=500, detail=f"Erro ao buscar o NCM: {str(e)}")
    else:
        return {"response": "limite máximo de pesquisas atingido"}

def clean_sql_response(sql_response):
    import re

    # Caso a entrada já seja uma lista de SQLs, retorna como está
    if isinstance(sql_response, list):
        return [sql.strip() for sql in sql_response]

    # Remove delimitadores de código
    sql_response = re.sub(r"^```(?:sql)?\n?|```$", "", sql_response, flags=re.IGNORECASE).strip()

    # Remove quebras de linha dentro dos SQLs, mas mantém ponto e vírgula como separador
    sql_response = re.sub(r"\n", " ", sql_response)

    # Divide múltiplos SQLs usando ponto e vírgula
    sql_list = [sql.strip() for sql in re.split(r";\s*", sql_response) if sql.strip()]

    return sql_list  # Retorna uma lista de SQLs




def execute_sql_queries(sql_queries):
    """
    Executa uma lista de consultas SQL no Firebird e retorna os resultados combinados.
    """
    con = firebirdsql.connect(
        host='localhost',
        database=bdP,
        port=3050,
        user='SYSDBA',
        password='masterkey',
        charset='WIN1252'  # Ajuste para o charset mais comum do banco
    )
    cur = con.cursor()

    results = []

    try:
        for sql_query in sql_queries:
            try:
                print(f"Executando SQL: {sql_query}")
                cur.execute(sql_query)
                columns = [desc[0] for desc in cur.description]  # Nome das colunas
                result = cur.fetchall()

                # Decodifica os resultados dinamicamente
                decoded_result = [
                    tuple(
                        safe_decode(item) for item in row
                    )
                    for row in result
                ]

                # Converte para DataFrame
                df = pd.DataFrame(decoded_result, columns=columns)
                results.append(df)  # Adiciona o DataFrame à lista de resultados
            except Exception as e:
                print(f"Erro ao executar SQL: {sql_query}\nErro: {e}")
                results.append(pd.DataFrame())  # Adiciona um DataFrame vazio em caso de erro

    finally:
        cur.close()
        con.close()

    return results  # Retorna uma lista de DataFrames


def safe_decode(value):
    """
    Decodifica valores dinamicamente, tratando problemas de encoding.
    - Tenta decodificar de 'latin1' para 'utf-8'.
    - Substitui caracteres inválidos para evitar erros.
    """
    try:
        if isinstance(value, bytes):  # Caso o dado seja binário
            return value.decode('utf-8', errors='replace')
        elif isinstance(value, str):  # Caso já seja string
            return value.encode('latin1', errors='replace').decode('utf-8', errors='replace')
        else:
            return value  # Retorna outros tipos diretamente (ex.: números)
    except Exception as e:
        print(f"Erro ao decodificar valor: {value}, Erro: {e}")
        return None  # Retorna None para valores problemáticos




def format_data_for_prompt(df, max_rows=10, max_columns=5):
    if df.empty:
        return "Nenhum dado encontrado para os critérios especificados."

    # Limitar linhas e colunas para não sobrecarregar o prompt
    df = df.iloc[:max_rows, :max_columns]

    # Converte para texto
    data_text = df.to_string(index=False)
    return data_text

def process_user_question(sql_queries, question):
    # Gera os SQLs limpos
    sql_list = clean_sql_response(sql_queries)

    # Executa cada SQL no banco de dados
    dataframes = execute_sql_queries(sql_list)
    if dataframes is None or all(df.empty for df in dataframes):
        return "Nenhum dado encontrado ou ocorreu um erro ao processar sua solicitação."

    # Formata os resultados para o prompt
    combined_data = []
    for idx, df in enumerate(dataframes):
        if df.empty:
            combined_data.append(f"Resultado {idx + 1}:\nNenhum dado encontrado.")
        else:
            formatted_data = format_data_for_prompt(df)
            combined_data.append(f"Resultado {idx + 1}:\n{formatted_data}")

    # Combina os resultados em um único texto
    combined_text = "\n\n".join(combined_data)

    # Gera a resposta final da IA
    response = querycreator(combined_text, question)
    return response
