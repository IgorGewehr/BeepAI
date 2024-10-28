from openAIConfig.openaiInit import initializeOpenAI

client = initializeOpenAI()

def querycreator(data, question):

    query = f"""Você é uma assistente virtual para me ajudar com dados do meu comércio, abaixo tem os dados do meu comércio"
    
    Article:
    \"\"\"
    {data}
    \"\"\"

    Question: {question}"""

    response = client.chat.completions.create(
        messages=[
            {'role': 'system', 'content': 'Sua resposta sobre meu comércio.'},
            {'role': 'user', 'content': query},
        ],
        model="gpt-3.5-turbo",
        temperature=0,
    )
    iareturn = response.choices[0].message.content
    return iareturn