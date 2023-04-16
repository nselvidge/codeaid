import os
from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.mapreduce import MapReduceChain
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.environ.get('OPENAI_API_KEY')

# load_dotenv()


def get_py_files(root_dir):
    paths = []
    # Recursively go through all files in directory
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.py'):
                file_path = os.path.join(dirpath, filename)
                paths.append(file_path)
    return paths


def get_py_text(py_path):
    # Read in a Markdown file
    with open(py_path, 'r') as f:
        markdown_text = f.read()
    f.close
    return markdown_text


def create_py_chunks(py_text):
    # Split Markdown text into chunks
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        "gpt2", chunk_size=3000, separator=".")
    md_chunks = splitter.split_text(py_text)
    return md_chunks


def get_py_summary(py_text):
    llm = OpenAI(temperature=0)
    texts = create_py_chunks(py_text)
    prompt_template = """Write a concise summary of the following python code
                    including inputs/outputs, imports/exports, and description of significant funcitons:
                        {text}
                    """
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
    try:
        chain = load_summarize_chain(
            llm, chain_type="map_reduce", map_prompt=PROMPT, combine_prompt=PROMPT)
        docs = [Document(page_content=t) for t in texts[:3]]
        output = chain({"input_documents": docs},
                       return_only_outputs=True)['output_text']
    except Exception as e:
        print(f'exception {e} with py_file {py_text}')
        chain = load_summarize_chain(llm, chain_type="stuff", prompt=PROMPT)
        docs = [Document(page_content=t) for t in texts[:3]]
        output = chain.run(docs)
    return output


# root_dir = './.data/langchain/'
# print('Python files found:', len(get_py_files(root_dir)))

# py_files = get_py_files(root_dir)
# py_text = get_py_text(py_files[50])
# summary = get_py_summary(py_text)
# print(summary['output_text'])
