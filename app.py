from datetime import datetime

from db import Database
from logger import logger
import json
import random

import flask
from flask import Flask, jsonify

app = Flask(__name__)
database = Database()

@app.route("/api/score-speech", methods=["POST"])
def api_score_speech():
    data = flask.request.json

    # validation
    if "company" not in data:
        return jsonify({
            "message": "company not provided"
        }), 400
    company = data["company"]

    if "text" not in data:
        return jsonify({
            "message": "text not provided"
        }), 400
    text = data["text"]

    # do stuff with data[text]

    response_data = {
        "score": random.randint(0, 100)
    }

    # cache result
    results_dict = database.data.get("results", {})
    results_dict[company] = results_dict.get(company, []) + [response_data["score"]]
    database.data["results"] = results_dict
    database.save_to_file()

    return jsonify(response_data)

@app.route("/api/rankings", methods=["GET"])
def api_rankings():
    response_data = database.data.get("results", {})
    # response_data = []
    # for company, scores in results.items():
    #     response_data.append({
    #         "company": company,
    #         "average_score": sum(scores)/len(scores) if len(scores) > 0 else 0
    #     })
    return jsonify(response_data)