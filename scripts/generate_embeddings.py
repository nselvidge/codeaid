import os
import numpy as np
import openai
from docarray import DocumentArray, Document
from dotenv import load_dotenv
import concurrent.futures

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = "us-west1-gcp"
INDEX_NAME = "test-2"
EMBEDDING_DIMENSION = 1536
PROJECT_NAME = "codeaid"
EMBEDDING_MODEL = "text-embedding-ada-002"

load_dotenv()
openai.api_key = os.environ.get('OPENAI_API_KEY')


def get_embedding(document):
    document.embedding = np.array(openai.Embedding.create(
        input=document.text, engine=EMBEDDING_MODEL)['data'][0]['embedding'])
    return document

def get_embedding_batch(batch):
    tmp = [j['embedding'] for j in openai.Embedding.create(
        input=[i.text for i in batch], engine=EMBEDDING_MODEL)['data']]
    for i, doc in enumerate(batch):
        doc.embedding = tmp[i]

def get_index_dir(repo):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    project_directory = os.path.dirname(script_directory)
    return f"{project_directory}/annlite/{repo}"

def get_index(repo):
    index = DocumentArray(storage='annlite', config={
                          'n_dim': EMBEDDING_DIMENSION, 'data_path': get_index_dir(repo), })
    return index

def generate_and_store_embeddings(repo: str, data: list[dict], batch_size=10, with_batching=False):
    """
    :input data: data is a list of dictionaries with the following keys 'id', 'text', 'metadata'
    """
    print(f'generating embeddings for {len(data)} documents')
    
    index = get_index(repo)

    index.clear()
    index.summary()

    documents = [Document(text=i['text'], id=i['id'],
                          metadata=i['metadata']) for i in data][:10]

    index.extend(documents)

    print(f'applying the embedding on {len(documents)} documents')
    if with_batching:
        batches = [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]
        get_embedding_batch(documents[:10])
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(get_embedding_batch, batches)
    else:
        index.apply(get_embedding, show_progress=True)
    index.summary()


def query(repo: str, prompt: str, top_k: int = 30):
    # create index
    index = get_index(repo=repo)
    document = Document(content=prompt)
    document = get_embedding(document=document)
    matches = index.find(document, metric='cosine', top_k=top_k)
    return matches[0]