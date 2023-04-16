import os
import time
import numpy as np
import openai
from docarray import DocumentArray, Document

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = "us-west1-gcp"
INDEX_NAME = "test-2"
EMBEDDING_DIMENSION = 1536
PROJECT_NAME = "codeaid"
EMBEDDING_MODEL = "text-embedding-ada-002"


def get_embedding(document):
    document.embedding = np.array(openai.Embedding.create(
        input=document.text, engine=EMBEDDING_MODEL)['data'][0]['embedding'])
    return document


def generate_and_store_embeddings(data: list[dict]):
    """
    :input data: data is a list of dictionaries with the following keys 'id', 'text', 'metadata'
    """
    index = DocumentArray(storage='annlite', config={
                          'n_dim': EMBEDDING_DIMENSION, 'data_path': '../annlite', })

    index.clear()

    documents = [Document(text=i['text'], id=i['id'],
                          metadata=i['metadata']) for i in data]

    index.extend(documents)

    index.apply(get_embedding)


def query(prompt: str, top_k: int = 30):
    # create index
    index = DocumentArray(storage='annlite', config={
                          'n_dim': EMBEDDING_DIMENSION, 'data_path': './annlite', })

    document = Document(content=prompt)
    document = get_embedding(document=document)
    matches = index.find(document, metric='cosine', top_k=top_k)

    print(index)
    return matches[0]
