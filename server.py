import os
from flask import Flask, request, jsonify, render_template


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
