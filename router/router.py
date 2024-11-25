from http.client import HTTPException

import firebirdsql
from fastapi import FastAPI, APIRouter, Query

from openAIConfig import querycreator
from openAIConfig.embeddings import create_ai_reply, check_ncm_similarity
from openAIConfig.queryCreator import queryNCMcreator, interpret_question
import fdb
import pandas as pd

router = APIRouter()

@router.get('/')
async def testserver():
    return {"response": "Servidor testado"}


@router.get("/askai")
async def get_askai(userQuestion: str = Query(...)):
    try:
        response = process_user_question(clean_sql_response(interpret_question(userQuestion)), userQuestion)
        return {"response": response}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Erro de validação: {str(ve)}")
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=f"Arquivo não encontrado: {str(fnf)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no servidor: {str(e)}")


@router.get("/askai/interpreted_query")
async def get_interpreted_query(userQuestion: str = Query(...)):
    try:
        response = clean_sql_response(interpret_question(userQuestion))

        return {"response": response}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Erro de validação: {str(ve)}")
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=f"Arquivo não encontrado: {str(fnf)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no servidor: {str(e)}")

@router.get("/askai/ncm/{diretorio_user}")
async def get_ncm(product_name: str):
    """
    Rota para buscar o NCM mais apropriado para o produto fornecido.

    Args:
        product_name (str): Nome do produto.

    Returns:
        str: Número do NCM mais relevante.
    """
    try:
        # Calcular similaridade e obter o contexto relevante
        similarity_df = check_ncm_similarity(product_name)
        top_ncm_data = similarity_df.head(1).to_dict('records')[0]  # Obtém a linha mais relevante

        # Gera a resposta do NCM
        response = queryNCMcreator(data=top_ncm_data, question=product_name)
        return {"ncm": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar o NCM: {str(e)}")


def clean_sql_response(sql_response):
    import re

    # Remove delimitadores de código (```sql, ```, etc.)
    sql_clean = re.sub(r'```[\s\S]*?```', '', sql_response).strip()
    sql_clean = re.sub(r'`{1,3}sql', '', sql_clean, flags=re.IGNORECASE).strip()
    sql_clean = re.sub(r'`{1,3}', '', sql_clean).strip()

    # Substitui sequências de escape \n por quebras de linha reais
    if '\\n' in sql_clean:  # Caso os caracteres sejam literais (\ + n)
        sql_clean = sql_clean.replace('\\n', '\n')
    else:  # Caso já sejam interpretados como quebras de linha
        sql_clean = sql_clean.replace('\n', ' ')

    # Remove espaços extras e quebras de linha adicionais
    sql_clean = re.sub(r'\s+', ' ', sql_clean).strip()

    return sql_clean


def execute_sql_query(sql_query):
    # Conexão com o banco de dados
    con = firebirdsql.connect(
        host='localhost',
        database='C:/App/db.fdb',
        port=3050,
        user='SYSDBA',
        password='masterkey',
        charset='UTF8'
    )
    cur = con.cursor()

    try:
        # Executa o SQL e obtém os dados
        cur.execute(sql_query)
        columns = [desc[0] for desc in cur.description]  # Nome das colunas
        result = cur.fetchall()

        # Converte para DataFrame para facilitar manipulação
        df = pd.DataFrame(result, columns=columns)
        return df
    except Exception as e:
        print(f"Erro ao executar a consulta SQL: {e}")
        return None
    finally:
        cur.close()
        con.close()


def format_data_for_prompt(df, max_rows=10, max_columns=5):
    if df.empty:
        return "Nenhum dado encontrado para os critérios especificados."

    # Limitar linhas e colunas para não sobrecarregar o prompt
    df = df.iloc[:max_rows, :max_columns]

    # Converte para texto
    data_text = df.to_string(index=False)
    return data_text

def process_user_question(sql_query, question):
    # Gera o SQL com base na pergunta
    clean_sql = clean_sql_response(sql_query)

    # Executa o SQL no banco de dados
    data = execute_sql_query(clean_sql)
    if data is None or data.empty:
        return "Nenhum dado encontrado ou ocorreu um erro ao processar sua solicitação."

    # Formata os dados para o prompt
    data_text = format_data_for_prompt(data)

    # Gera a resposta final da IA
    response = querycreator(data_text, question)
    return response
