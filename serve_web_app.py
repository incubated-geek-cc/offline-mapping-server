import requests 

from flask import Flask
from flask import render_template
from flask import request
from werkzeug.wrappers import Request, Response

def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    
app = Flask(__name__)
@app.route("/")
def index():
    title="Local Basemap"
    return render_template("index.html", message=title, template_folder="templates", static_folder="static")

@app.route("/shutdown", methods=["GET"])
def shutdown():
    shutdown_server()
    return "Server shutting down..."

if __name__ == "__main__":
    from werkzeug.serving import run_simple
    run_simple("localhost", 9000, app)