from datetime import datetime

import db
from logger import logger
import json
import random

import flask
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/score-speech", methods=["POST"])
def api_score_speech():
    data = flask.request.json
    # do stuff with data[text]
    return jsonify({
        "score": random.randint(0, 100)
    })
