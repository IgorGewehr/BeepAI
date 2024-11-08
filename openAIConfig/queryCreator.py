from openAIConfig.openaiInit import initializeOpenAI

client = initializeOpenAI()

def querycreator(data, question):

    query = f"""Você é uma assistente virtual para me ajudar com dados do meu comércio, abaixo tem os dados do meu comércio
    Nos dados que terá acesso lembresse de nunca trazer informações na sua resposta que sejam IDs, nem ID de vendas ou produtos, nada, apenas códigos, opte por códigos 
    ou outras informações úteis, tente trazer também respostas mais curtas e objetivas, porém que sejam prestativas, por exemplo, se eu lhe pedir o .
    meu produto mais caro, você me responde com o código do produto, seu preço de custo e seu preço de venda, etc.
    
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