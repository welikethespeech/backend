from google.cloud import language_v1
from math import exp
import os
import json

json_str = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
json_data = json.loads(json_str)
json_data['private_key'] = json_data['private_key'].replace('\\n', '\n')
credentials = service_account.Credentials.from_service_account_info(
    json_data)
client = language_v1.LanguageServiceClient(credentials)
good_words = set(["environment", "ocean", "trees", "solar power", "wind power", "renewables", "sustainable", "sustainability"])
bad_words = set(["plastic", "fossil fuel", "fossil fuels", "carbon dioxide", "methane", "waste"])

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
    temp_score = 0
    for entity in entities:
        name = entity.name
        sentiment = entity.sentiment
        entity_score = sentiment.score
        entity_mag = sentiment.magnitude
        if name in good_words:
            temp_score += entity_score
        elif name in bad_words:
            temp_score -= entity_score
    return 100/(1+exp(-temp_score))
