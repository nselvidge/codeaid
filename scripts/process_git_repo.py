"""This script pulls the latest code from a git repo"""
import subprocess
import os
from md_parser import get_md_files, get_md_text

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

    print("Done running markdown parser, running embedding generator")

    # run embedding generator

    print("Done running embedding generator, uploading embeddings to pinecone")

    # upload embeddings to pinecone

    print("Done")


pull_git_repo()
