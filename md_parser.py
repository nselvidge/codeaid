import os

def get_md_files(root_dir):
    paths = []
    # Recursively go through all files in directory
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.md'):
                file_path = os.path.join(dirpath, filename)
                paths.append(file_path)
    return paths

def get_md_text(md_path):
    # Read in a Markdown file
    with open(md_path, 'r') as f:
        markdown_text = f.read()
    f.close
    return markdown_text

# root_dir = './langchain/'
# print('Markdown files found:', len(get_md_files(root_dir)))
# print(get_md_text(get_md_files(root_dir)[1]))