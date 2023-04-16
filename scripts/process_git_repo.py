"""This script pulls the latest code from a git repo"""
import subprocess
import os
from md_parser import get_md_files, get_md_text, create_md_chunks
from py_parser import get_py_files, get_py_text, get_py_summary
from generate_embeddings import generate_and_store_embeddings

REPO_NAME = 'llamaindex'
REPO_URL = "https://github.com/jerryjliu/llama_index"


def pull_git_repo():
    """Pulls the latest code from the git repo"""
    print("Pulling latest code from git repo")
    # clone repo into .data folder
    target_dir = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)), f"../.data/{REPO_NAME}")

    os.makedirs(target_dir, exist_ok=True)
    subprocess.call(["git", "clone", REPO_URL], cwd=target_dir)

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

    print(f"Found {len(md_chunks)} chunks of markdown text")

    # run python parser
    py_files = get_py_files(target_dir)
    py_summary = []
    for i, py_file in enumerate(py_files):
        py_text = get_py_text(py_file)
        summary = get_py_summary(py_text)
        py_summary.append({
                'id': f"{py_file.split('.data')[1]}-{i}",
                'text': summary['output_text'],
                'metadata': {
                    'file_path': py_file,
                }
            })

    print("Done running markdown parser, running embedding generator")

    # run embedding generator
    generate_and_store_embeddings(REPO_NAME, md_chunks)

    print("Done")


pull_git_repo()
