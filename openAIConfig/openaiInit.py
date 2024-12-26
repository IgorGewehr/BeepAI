from openai import OpenAI

def initializeOpenAI():
    client = OpenAI(
        api_key='Sua-Chave')
    return client