from google.cloud import language_v1
from math import exp
import os
import json
from google.oauth2 import service_account

json_str = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
json_data = json.loads(json_str)
json_data['private_key'] = json_data['private_key'].replace('\\n', '\n')
credentials = service_account.Credentials.from_service_account_info(
    json_data)
client = language_v1.LanguageServiceClient(credentials=credentials)

good_words = set(["environment", "ocean", "trees", "solar power", "wind power", "renewables", "sustainable", "sustainability", "tidal", "solar", "wind"])
bad_words = set(["plastic", "fossil fuel", "fossil fuels", "carbon dioxide", "methane", "waste", "oil", "petrol", ""])
environment_categories = set(["/Science/Ecology & Environment", "/Science/Ecology & Environment/Climate Change & Global Warming", "/People & Society/Social Issues & Advocacy/Green Living & Environmental Issues"])

def analyze_entity_sentiment(text_content):
    """
    Analyzing Entity Sentiment in a String

    Args:
      text_content The text content to analyze
    """

    type_ = language_v1.types.Document.Type.PLAIN_TEXT

    document = {"content": text_content, "type_": type_}

    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_entity_sentiment(request = {'document': document, 'encoding_type': encoding_type})

    return response.entities

def classify_text(text_content):
    """
    Classifying Content in a String

    Args:
      text_content The text content to analyze. Must include at least 20 words.
    """

    type_ = language_v1.Document.Type.PLAIN_TEXT

    document = {"content": text_content, "type_": type_}

    response = client.classify_text(request = {'document': document})
    return response.categories

def analyze_sentiment(text_content):
    """
    Analyzing Sentiment in a String

    Args:
      text_content The text content to analyze
    """


    type_ = language_v1.Document.Type.PLAIN_TEXT

    document = {"content": text_content, "type_": type_}

    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_sentiment(request = {'document': document, 'encoding_type': encoding_type})

    return (response.document_sentiment, response.sentences)

def process_text(text): # Returns score from 0-100 representing sustainability
    entities = analyze_entity_sentiment(text)
    try:
        categories = classify_text(text)
    except:
        categories = None
    #sentiment, sentences = analyze_sentiment(text)
    entities_score = 0
    category_score = 0
    total_entities_counted = 0
    for entity in entities:
        name = entity.name
        sentiment = entity.sentiment
        entity_score = sentiment.score
        entity_mag = sentiment.magnitude
        if name in good_words:
            entities_score += entity_score
            total_entities_counted += 1
        elif name in bad_words:
            entities_score -= entity_score
            total_entities_counted += 1
    entities_score = entities_score / total_entities_counted
    entities_score = ((entities_score / 2) + 1) * 100
    if categories:
        for category in categories:
            if category.confidence > 0.5 and category.name in environment_categories:
                category_score += 200/3
                break
    if categories:
        total_score = entities_score * 0.7 + category_score * 0.3
    else:
        total_score = entities_score
    return total_score
