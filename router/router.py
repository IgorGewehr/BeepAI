from http.client import HTTPException

from fastapi import FastAPI, APIRouter

from openAIConfig.embeddings import create_ai_reply

router = APIRouter()

@router.get('/')
async def testserver():
    return {"response": "Servidor ativo"}


@router.get("/askai")
async def get_askai(userQuestion: str):
    try:
        # Tenta gerar a resposta
        response = create_ai_reply(userQuestion)
        return {"response": response}
    except ValueError as ve:
        # Erros de validação ou dados inválidos
        raise HTTPException(status_code=400, detail=f"Erro de validação: {str(ve)}")
    except FileNotFoundError as fnf:
        # Erros relacionados a arquivos (ex. CSV não encontrado)
        raise HTTPException(status_code=404, detail=f"Arquivo não encontrado: {str(fnf)}")
    except Exception as e:
        # Qualquer outro erro inesperado
        raise HTTPException(status_code=500, detail=f"Erro no servidor: {str(e)}")

