import os
import yaml
from flask import Flask, request, jsonify, render_template, Response

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
            'description': 'A plugin that analyzes and summarizes your code repos using ChatGPT.',
            'version': 'v1',
        },
        'paths': {
            '/search': {
                'get': {
                    'operationId': 'searchQuery',
                    'summary': 'Answers questions about the codebase to help users understand its functionality',
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


@ app.route('/search', methods=['POST'])
def search():
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({'error': 'Missing or invalid payload'}), 400

    text = data['text']

    # Perform your search or processing here
    result = f'You searched for: {text}'

    return jsonify({'result': result})


if __name__ == '__main__':
    app.run(debug=True)
