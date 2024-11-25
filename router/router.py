from http.client import HTTPException

from fastapi import FastAPI, APIRouter, Query

from openAIConfig.embeddings import create_ai_reply, check_ncm_similarity
from openAIConfig.queryCreator import queryNCMcreator, interpret_question

router = APIRouter()

@router.get('/')
async def testserver():
    return {"response": "Servidor testado"}


@router.get("/askai")
async def get_askai(userQuestion: str = Query(...), context: str = Query(...)):
    try:
        response = create_ai_reply(userQuestion, context)
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
        response = interpret_question(userQuestion)
        return {"response": response}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Erro de validação: {str(ve)}")
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=f"Arquivo não encontrado: {str(fnf)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no servidor: {str(e)}")

@router.get("/askai/ncm")
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