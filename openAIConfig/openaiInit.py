from openai import OpenAI

def initializeOpenAI():
    client = OpenAI(
        api_key='chave openai')
    return client