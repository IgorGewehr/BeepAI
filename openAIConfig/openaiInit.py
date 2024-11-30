from openai import OpenAI

def initializeOpenAI():
    client = OpenAI(
        api_key='key')
    return client