from pathlib import Path
from flask import Flask, render_template, request, jsonify
import backend
from configurations import DevelopmentConfig
from constants import *

app = Flask(__name__, static_folder="static")
app.config.from_object(DevelopmentConfig)

@app.context_processor
def inject_context():
    return dict()

@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

@app.route("/chat", methods=["POST"])
def send_chat():
    # TODO: Decompose response and convert into message history for backend
    pass

if __name__ == "__main__":
    app.run(debug=True,
            host="localhost",
            port=4007
    )