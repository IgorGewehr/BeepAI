from openai import OpenAI

def initializeOpenAI(key):
    client = OpenAI(
        api_key=key)
    return client