from datetime import datetime

import string
from db import Database
from logger import logger
import json
import random
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_cors import CORS, cross_origin

import flask
from flask import Flask, jsonify

from cloud_api import process_text

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per second"]
)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
database = Database()

@app.route("/api/score-speech", methods=["POST"])
@cross_origin()
def api_score_speech():
    data = flask.request.json

    # validation
    if "company" not in data:
        return jsonify({
            "message": "company not provided"
        }), 400
    company = data["company"].strip().lower()

    # check if company is valid string
    if not all([(c in string.ascii_letters + string.digits + " ") for c in company]):
        return jsonify({
            "message": "invalid company name, please only use letters, digits and spaces"
        }), 400

    if len(company) <= 0:
        return jsonify({
            "message": "company not provided"
        }), 400

    if "text" not in data:
        return jsonify({
            "message": "text not provided"
        }), 400
    text = data["text"]

    # do stuff with data[text]

    response_data = {
        "score": round(process_text(text), 2)
    }

    # cache result
    results_dict = database.data.get("results", {})
    results_dict[company] = results_dict.get(company, []) + [response_data["score"]]
    database.data["results"] = results_dict
    database.save_to_file()

    return jsonify(response_data)

@app.route("/api/rankings", methods=["GET"])
@cross_origin()
def api_rankings():
    database.load_from_file()
    response_data = database.data.get("results", {})
    # response_data = []
    # for company, scores in results.items():
    #     response_data.append({
    #         "company": company,
    #         "average_score": sum(scores)/len(scores) if len(scores) > 0 else 0
    #     })
    return jsonify(response_data)
