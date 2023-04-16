import os
import yaml
from flask import Flask, request, jsonify, render_template, Response
from scripts.generate_embeddings import query

app = Flask(__name__)
host = os.environ.get("HOST", "http://localhost")


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
        "description_for_model": "Plugin to help you understand an open source"
        " repository.",
        "auth": {
            "type": "none"
        },
        "api": {
            "type": "openapi",
            "url": f"{host}/openapi.yaml",
            "is_user_authenticated": False
        },
        "logo_url": f"{host}/logo.png",
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
                            'description': 'The name of the repo. Only llamaindex or langchain are supported for now.',
                            'required': True,
                            'schema': {
                                'type': 'string',
                                'enum': ['llamaindex', 'langchain'],
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


if __name__ == '__main__':
    app.run(debug=True)
