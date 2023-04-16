"""This script pulls the latest code from a git repo"""
import subprocess
import os
from scripts.md_parser import get_md_files, get_md_text, create_md_chunks
from scripts.py_parser import get_py_files, get_py_text, get_py_summary
from scripts.generate_embeddings import generate_and_store_embeddings, get_root_index
from tqdm.auto import tqdm

# REPO_NAME = 'llamaindex'
# repo_name = 'langchain'
# REPO_URL = "https://github.com/jerryjliu/llama_index"
# repo_url = "https://github.com/hwchase17/langchain.git"

def find_folders_in_directory(directory):
    folders = [entry.name for entry in os.scandir(directory) if entry.is_dir()]
    return folders

def is_indexed(repo_name):
    index_dir = get_root_index()
    indexed_repos = find_folders_in_directory(index_dir)
    print(indexed_repos)
    is_indexed = repo_name in indexed_repos
    return is_indexed

def pull_git_repo(repo_name, repo_url, include_pydocs=False, include_summary=False, with_batching=False):
    """Pulls the latest code from the git repo"""
    ind = is_indexed(repo_name)
    if not ind:
        # clone repo into .data folder
        target_dir = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)), f"../.data/{repo_name}")

        os.makedirs(target_dir, exist_ok=True)
        subprocess.call(["git", "clone", repo_url], cwd=target_dir)

        print("Done pulling latest code from git repo, running markdown parser")

        # run markdown parser
        md_files = get_md_files(target_dir)
        md_chunks = []
        for md_file in md_files:
            md_text = get_md_text(md_file)
            current_chunks = create_md_chunks(md_text)

            for i, chunk in enumerate(current_chunks):
                md_chunks.append({
                    'id': f"{md_file.split('.data')[1]}-{i}",
                    'text': chunk,
                    'metadata': {
                        'file_path': md_file,
                    }
                })

        print(f"Found {len(md_chunks)} chunks of markdown text in {repo_name}")

        # run python parser
        py_files = get_py_files(target_dir)
        py_summary = []
        l_py_file_err = []
        if include_pydocs:
            for i, py_file in tqdm(enumerate(py_files)):
                try:
                    py_text = get_py_text(py_file)
                    if include_summary:
                        summary = get_py_summary(py_text)
                        py_summary.append(
                            {
                            'id': f"summary-{py_file.split('.data')[1]}-{i}",
                            'text': summary,
                            'metadata': {
                                'file_path': py_file,
                            }
                        }
                        )
                    py_summary.append(
                        
                        {
                            'id': f"{py_file.split('.data')[1]}-{i}",
                            'text': py_text,
                            'metadata': {
                                'file_path': py_file,
                            }
                        }
                    )
                except Exception as exc:
                    print(f'ERROR for python file {py_file}: {exc}')
                    l_py_file_err.append(py_file)

        print(f"finished parsing code. {len(py_summary)} in {repo_name}")

        # run embedding generator
        generate_and_store_embeddings(repo_name, md_chunks + py_summary, with_batching=with_batching)
        return ind
    else:
        print('Repo already indexed')
        return ind
        


if __name__ == "__main__":
    import time 
    t1 = time.time()
    pull_git_repo(
        repo_name='langchain',
        repo_url='https://github.com/hwchase17/langchain.git',
        include_pydocs=True,
        with_batching=False
    )
    t2 = time.time()
    print(f'time taken without batching: {t2 - t1}')
    pull_git_repo(
        repo_name='langchain',
        repo_url='https://github.com/hwchase17/langchain.git',
        include_pydocs=True,
        with_batching=True
    )
    t3 = time.time()
    print(f'time taken with batching: ', t3 - t2)    
