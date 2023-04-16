import os
import yaml
from flask import Flask, request, jsonify, render_template, Response
from scripts.generate_embeddings import query 
from scripts.process_git_repo import pull_git_repo
from scripts.repo_finder import find_repos

app = Flask(__name__)
# host = os.environ.get("HOST", "http://localhost")
host = "https://zakariaelh-legendary-space-invention-5x69wqw7p724w7-5000.preview.app.github.dev/"

def find_folders_in_directory(directory):
    folders = [entry.name for entry in os.scandir(directory) if entry.is_dir()]
    return folders

@app.route("/", methods=["GET"])
def hello_world():
    return render_template('index.html')


@app.route("/.well-known/ai-plugin.json")
def plugin_json():
    """Return the plugin.json file for the plugin with current host"""
    return {
        "schema_version": "v1",
        "name_for_human": "CodeAid Plugin",
        "name_for_model": "codeaid",
        "description_for_human": "Plugin to help you understand an open source"
        " repository.",
        "description_for_model": "Plugin to help you understand an open source."
        " repository.",
        "auth": {
            "type": "none"
        },
        "api": {
            "type": "openapi",
            "url": f"{host}/openapi.yaml",
            "is_user_authenticated": False
        },
        "logo_url": f"{host}/static/logo.png",
        "contact_email": "support@example.com",
        "legal_info_url": f"{host}/legal"
    }


@app.route('/openapi.yaml', methods=['GET'])
def openapi_yaml():
    openapi_spec = {
        'openapi': '3.0.1',
        'info': {
            'title': 'CodeAid',
            'description': 'A plugin that provides context and documentation for open source codebases. Currently only supports the llamaindex and langchain repos.',
            'version': 'v1',
        },
        'paths': {
            '/search': {
                'get': {
                    'operationId': 'searchQuery',
                    'summary': 'Answers questions about the codebase to help users understand its functionality',
                    'parameters': [
                        {
                            'name': 'query',
                            'in': 'query',
                            'description': 'A question about the codebase',
                            'required': True,
                            'schema': {
                                'type': 'string',
                            },
                        }, {

                            'name': 'repo',
                            'in': 'query',
                            'description': 'The name of the repo.',
                            'required': True,
                            'schema': {
                                'type': 'string',
                                # 'enum': ['llamaindex', 'langchain'],
                            },
                        }],
                    'responses': {
                        '200': {
                            'description': 'OK',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        '$ref': '#/components/schemas/searchQueryResponse',
                                    },
                                },
                            },
                        },
                    },
                },
            },
            '/load': {
                'get': {
                    'operationId': 'searchQuery2',
                    'summary': 'Use this endpoint when the user gives a github link. It triggers a job that will index the codebase in the backend',
                    'parameters': [
                        {
                            'name': 'url',
                            'in': 'query',
                            'description': 'Triggers a job in the backend',
                            'required': True,
                            'schema': {
                                'type': 'string',
                            },
                        }, {

                            'name': 'name',
                            'in': 'query',
                            'description': 'The name of the repo. Infer it from the url',
                            'required': True,
                            'schema': {
                                'type': 'string'
                            },
                        }],
                    'responses': {
                        '200': {
                            'description': 'OK',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        '$ref': '#/components/schemas/searchQueryResponse',
                                    },
                                },
                            },
                        },
                    },
                },
            },
            '/search_repo': {
                'get': {
                    'operationId': 'searchQuery3',
                    'summary': 'Use this endpoint when the you re not familiar with library or repo that the user is talking about to find repos on github.',
                    'parameters': [
                        {
                            'name': 'library_name',
                            'in': 'query',
                            'description': 'Looks for repos of a library in github',
                            'required': True,
                            'schema': {
                                'type': 'string',
                            },
                        }],
                    'responses': {
                        '200': {
                            'description': 'OK',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        '$ref': '#/components/schemas/searchQueryResponse',
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        'components': {
            'schemas': {
                'searchQueryRequest': {
                    'type': 'object',
                    'properties': {
                        'query': {
                            'type': 'string',
                            'description': 'A question about the codebase',
                            'required': 'true',
                        },
                        'repo': {
                            'type': 'string',
                            'enum': ['llamaindex', 'langchain'],
                            'description': 'The name of the repo. Only llamaindex or langchain are supported for now.',
                            'required': 'true',
                        }
                    },
                },
                'searchQuery2Request': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'description': 'The name of the repo. Infer it from the url',
                            'required': 'true',
                        },
                        'repo': {
                            'type': 'url',
                            'description': 'The url of the repo',
                            'required': 'true',
                        }
                    },
                },
                'searchQuery3Request': {
                    'type': 'object',
                    'properties': {
                        'library_name': {
                            'type': 'string',
                            'description': 'The name of the repo/ library you dont about.',
                            'required': 'true',
                        }
                    },
                },
                'searchQueryResponse': {
                    'type': 'object',
                    'properties': {
                        'text': {
                            'type': 'string',
                            'description': 'A detailed answer or relevant information about the queried aspect of the codebase',
                        },
                        'timestamp': {
                            'type': 'string',
                            'format': 'date-time',
                            'description': 'The timestamp of the response.',
                        },
                    },
                },
            },
        }}

    yaml_content = yaml.dump(openapi_spec, sort_keys=False)
    return Response(yaml_content, content_type='application/x-yaml')


@ app.route('/search', methods=['GET'])
def search():
    print('searching')
    data = request.args
    print(data)

    if not data or 'query' not in data:
        return jsonify({'error': 'Missing or invalid payload'}), 400

    text = data['query']
    repo = data['repo']
    documents = query(repo, text)
    dictionary = [{'text': text} for text in documents[:, 'text']]
    print(dictionary)
    return jsonify(dictionary)


@ app.route('/load', methods=['GET'])
def load():
    data = request.args
    print(f'load repo endpoint. data: {data}')
    if not data or 'url' not in data:
        return jsonify({'error': 'Missing or invalid payload'}), 400

    repo_url = data['url']
    repo_name = data['name']
    pull_git_repo(
        repo_name=repo_name,
        repo_url=repo_url,
        include_summary=False,
        include_pydocs=True,
        with_batching=True
    )
    resp = [
        {
            'text': f'your repo {repo_url} has been index successfully. Feel free to ask any questions about it.'
        }
    ]
    return jsonify(resp)


@ app.route('/search_repo', methods=['GET'])
def search_repo():
    data = request.args
    print(f'load repo endpoint. data: {data}')
    if not data or 'library_name' not in data:
        return jsonify({'error': 'Missing or invalid payload'}), 400

    repo_name = data['library_name']
    dict_repos = find_repos(name=repo_name)
    
    resp = [
        {
            'text': f'We found {len(dict_repos)} on github that match the library name {repo_name}. which one would you like to index? If none of these match the library you re looking for, please enter the url of your repo and we ll index it promptly. {dict_repos}',
        }
    ]
    return jsonify(resp)

if __name__ == '__main__':
    app.run(debug=True)
