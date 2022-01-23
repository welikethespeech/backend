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

import os

import flask
from flask import Flask, jsonify

from cloud_api import process_text
from speech import transcribe
import traceback

from websitescrape import scrape

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["5 per second"]
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

    if len(text) > 1999:
        return jsonify({
            "message": f"text too long -- {len(text)}"
        }), 400

    # do stuff with data[text]
    cached_processed = database.data.get("processed", {})
    if text in cached_processed:
        print("Picked up from cache.")
        response_data = cached_processed.get(text, {})
    else:
        processed = process_text(text)
        response_data = {
            "score": round(processed["score"], 2),
            "highlighted": processed["highlighted"]
        }
        database.data.get("processed", {})[text] = response_data
        database.save_to_file()

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
    # response_data = database.data.get("results", {})
    results = database.data.get("results", {})
    response_data = []
    for company, scores in results.items():
        response_data.append({
            "company": company,
            "average_score": sum(scores)/len(scores) if len(scores) > 0 else 0
        })

    response_data = list(sorted(response_data, key=lambda elm: elm["average_score"]))
    return jsonify(response_data)

@app.route("/api/transcribe", methods=["POST"])
@cross_origin()
def api_transcribe():
    data = flask.request.json
    if "url" not in data:
        return jsonify({"message": "url not provided"}), 400
    url = data["url"]

    try:
        transcription_data = transcribe(url)
        logger.debug(f"transcription data get: {transcription_data}")
        actual_data = transcription_data["results"]["channels"][0]["alternatives"][0]
        return jsonify({
            "transcription": actual_data["transcript"],
            "confidence": actual_data["confidence"],
        })
    except:
        traceback.print_exc()
        return jsonify({"message": "A fatal exception occurred. Try using a shorter video"}), 400

@app.route("/api/websitescrape", methods=["POST"])
@cross_origin()
def api_websitescrape():
    data = flask.request.json
    if "url" not in data:
        return jsonify({"message": "url not provided"}), 400
    url = data["url"]

    try:
        scraped_data = scrape(url)
        logger.debug(f"website scrape data get: {scraped_data}")
        return jsonify({
            "scraped": scraped_data
        })
    except:
        traceback.print_exc()
        return jsonify({"message": "a fatal exception occurred"}), 400

@app.route("/api/nuke", methods=["POST"])
@cross_origin()
def api_nuke():
    target_code = os.environ.get('SECRET_KEY')
    data = flask.request.json
    if "SECRET_KEY" in data:
        secret = data["SECRET_KEY"]
        if secret == target_code:
            return jsonify({"message": "nuking test works"})
    
