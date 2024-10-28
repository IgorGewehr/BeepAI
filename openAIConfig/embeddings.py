from openAIConfig.openaiInit import initializeOpenAI
import os.path
import pandas as pd
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
from openAIConfig.queryCreator import querycreator

# Initialize the OpenAI client
client = initializeOpenAI()

# Função que carrega o CSV
try:
    df = pd.read_csv('C:/App/data_exported.csv', encoding='cp1252', delimiter=';')
except FileNotFoundError as e:
    raise FileNotFoundError(f"Erro: Arquivo CSV não encontrado no caminho especificado. {str(e)}")
except Exception as e:
    raise Exception(f"Erro ao carregar o arquivo CSV: {str(e)}")

# Função para obter o embedding (inclui tratamento de erro)
def get_embedding(text, model="text-embedding-3-small"):
    try:
        text = text.replace("\n", " ")
        return client.embeddings.create(input=[text], model=model).data[0].embedding
    except Exception as e:
        raise Exception(f"Erro ao gerar embedding: {str(e)}")

# Função para gerar o embedding da pergunta do usuário
def get_df_question(userQuestion):
    try:
        question_embedding = get_embedding(userQuestion)
        return np.array(question_embedding)
    except Exception as e:
        raise Exception(f"Erro ao gerar embedding da pergunta do usuário: {str(e)}")

# Função para gerar os embeddings do contexto (dados do comércio)
def get_df_context(df):
    try:
        if os.path.exists('C:/App/data_with_embeddings.csv'):
            print("Loading context embeddings from CSV file...")
            df_embeddings = pd.read_csv(
                'C:/App/data_with_embeddings.csv',
                converters={'embedding': json.loads}
            )
            df['embedding'] = df_embeddings['embedding']
        else:
            print("Calculating context embeddings...")
            # Concatena todas as colunas em uma única string por linha
            df['combined_text'] = df.astype(str).agg(' '.join, axis=1)
            # Gera embeddings para cada linha
            df['embedding'] = df['combined_text'].apply(lambda x: get_embedding(x))
            # Salva embeddings no CSV
            df_embeddings = df[['embedding']].copy()  # Cria uma cópia explícita para evitar warning
            df_embeddings['embedding'] = df_embeddings['embedding'].apply(json.dumps)
            df_embeddings.to_csv('C:/App/data_with_embeddings.csv', index=False)
        return df
    except FileNotFoundError as fnf:
        raise FileNotFoundError(f"Erro: Arquivo de embeddings não encontrado: {str(fnf)}")
    except Exception as e:
        raise Exception(f"Erro ao gerar ou carregar os embeddings do contexto: {str(e)}")

# Função para calcular a similaridade entre a pergunta e os dados
def check_similarity(question_embedding, context_df):
    try:
        context_embeddings = np.array(context_df['embedding'].tolist())
        similarities = cosine_similarity([question_embedding], context_embeddings).flatten()
        context_df['similarity'] = similarities
        return context_df.sort_values(by='similarity', ascending=False)
    except KeyError as ke:
        raise KeyError(f"Erro: Coluna de embeddings ausente no DataFrame: {str(ke)}")
    except Exception as e:
        raise Exception(f"Erro ao calcular similaridade: {str(e)}")

# Função para extrair os dados mais relevantes com base na similaridade
def answer_context(similarity_df, top_n=5):
    try:
        top_similar = similarity_df.head(top_n)
        data_columns = [col for col in top_similar.columns if col not in ['embedding', 'similarity', 'combined_text']]
        data = top_similar[data_columns]
        return data.to_string(index=False)
    except Exception as e:
        raise Exception(f"Erro ao extrair dados relevantes: {str(e)}")

# Função principal que integra tudo
def create_ai_reply(userQuestion):
    try:
        question_embedding = get_df_question(userQuestion)
        context_df = get_df_context(df)
        similarity_df = check_similarity(question_embedding, context_df)
        data = answer_context(similarity_df)
        response = querycreator(data, userQuestion)
        return response
    except Exception as e:
        raise Exception(f"Erro ao criar a resposta da IA: {str(e)}")
