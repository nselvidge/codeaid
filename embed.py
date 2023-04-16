import os
import time
import openai
import pinecone

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = "us-west1-gcp"
INDEX_NAME = "test-2"
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDING_DIMENSION = 1536
PROJECT_NAME = "codeaid"

openai.api_key = OPENAI_API_KEY


def get_index(index_name):
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENV,
        project_name=PROJECT_NAME  # find next to API key
    )
    # check if index already exists (it shouldn't if this is first time)
    if index_name not in pinecone.list_indexes():
        print('Index does not exist. Creating new index.')
        # if does not exist, create index
        pinecone.create_index(
            index_name,
            dimension=EMBEDDING_DIMENSION,
            metric='cosine',
            metadata_config={
                'indexed': ['file_name']
            }
        )
    # connect to index
    index = pinecone.Index(index_name)
    # view index stats
    return index


def retry_decorator(max_retries=3, delay_secs=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        print(
                            f"Function {func.__name__} failed after {max_retries} retries.")
                        raise e
                    else:
                        print(
                            f"Function {func.__name__} failed. Retrying... ({retries}/{max_retries})")
                        time.sleep(delay_secs)
        return wrapper
    return decorator


# @retry_decorator(max_retries=3, delay_secs=5)
def generate_embeddings_batch(list_text: list[str], embed_model: str = "text-embedding-ada-002") -> list[list[float]]:
    res = openai.Embedding.create(input=list_text, engine=embed_model)
    embeds = [record['embedding'] for record in res['data']]
    return embeds


def generate_and_store_embeddings(data: list[dict], batch_size=100):
    """
    :input data: data is a list of dictionaries with the following keys 'id', 'text', 'metadata'
    """
    # get index
    # split data into batches of batch_size
    batches = [data[i:i + batch_size] for i in range(0, len(data), batch_size)]
    print(f'Number of batches: {len(batches)}')
    # embed and store one batch at a time
    for batch in batches:
        # get ids
        ids = [i['id'] for i in batch]
        texts = [i['text'] for i in batch]
        metadata = [i['metadata'] for i in batch]
        # embed data
        embeds = generate_embeddings_batch(
            list_text=texts
        )
        to_upsert = list(zip(ids, embeds, metadata))
        index = get_index(index_name=INDEX_NAME)
        index.upsert(to_upsert)
