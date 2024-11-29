from openai import OpenAI

def initializeOpenAI():
    client = OpenAI(
        api_key='sua_chave')
    return client