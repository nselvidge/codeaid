"""This script pulls the latest code from a git repo"""
import subprocess
import os
from md_parser import get_md_files, get_md_text, create_md_chunks
from generate_embeddings import generate_and_store_embeddings

REPO_URL = "https://github.com/hwchase17/langchain"


def pull_git_repo():
    """Pulls the latest code from the git repo"""
    print("Pulling latest code from git repo")
    # clone repo into .data folder
    target_dir = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)), "../.data")

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
    
    print("Done running markdown parser, running embedding generator")

    # run embedding generator
    generate_and_store_embeddings(
        [md_chunks[10], md_chunks[15], md_chunks[20]])

    print("Done running embedding generator, uploading embeddings to pinecone")

    # upload embeddings to pinecone

    print("Done")


pull_git_repo()
