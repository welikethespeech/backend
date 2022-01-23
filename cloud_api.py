from google.cloud import language_v1
from math import exp
import os
import json
from google.oauth2 import service_account
import string

json_str = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
json_data = json.loads(json_str)
json_data['private_key'] = json_data['private_key'].replace('\\n', '\n')
credentials = service_account.Credentials.from_service_account_info(
    json_data)
client = language_v1.LanguageServiceClient(credentials=credentials)

good_words = set(["environment", "ocean", "trees", "solar power", "wind power", "renewables", "sustainable", "sustainability", "tidal", "solar", "wind", "earth", "air", "forest", "forests", "rainforest", "rainforests", "plant", "plants", "healthy", "grasslands", "clean energy", "water", "hydro", "nuclear", "tree", "renewable", "renewable energy"])
bad_words = set(["plastic", "fossil fuel", "fossil fuels", "carbon dioxide", "methane", "waste", "oil", "petrol", "pollution", "coal", "deforestation", "global warming", "greenhouse gas", "greenhouse gases", "fracking"])
environment_categories = set(["/Science/Ecology & Environment", "/Science/Ecology & Environment/Climate Change & Global Warming", "/People & Society/Social Issues & Advocacy/Green Living & Environmental Issues"])

def analyze_entity_sentiment(text_content, type_):
    """
    Analyzing Entity Sentiment in a String

    Args:
      text_content The text content to analyze
    """

    document = {"content": text_content, "type_": type_}

    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_entity_sentiment(request = {'document': document, 'encoding_type': encoding_type})

    return response.entities

def classify_text(text_content, type_):
    """
    Classifying Content in a String

    Args:
      text_content The text content to analyze. Must include at least 20 words.
    """

    document = {"content": text_content, "type_": type_}

    response = client.classify_text(request = {'document': document})
    return response.categories

def analyze_sentiment(text_content, type_):
    """
    Analyzing Sentiment in a String

    Args:
      text_content The text content to analyze
    """

    document = {"content": text_content, "type_": type_}

    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_sentiment(request = {'document': document, 'encoding_type': encoding_type})

    return (response.document_sentiment, response.sentences)

def process(entities, categories, sentiment, sentences):
    entities_score = 0
    category_score = 0
    sentiment_score = 0
    total_entities_counted = 0
    highlight_sentences = {}
    for entity in entities:
        name = entity.name.lower()
        sentiment = entity.sentiment
        entity_score = sentiment.score
        entity_mag = sentiment.magnitude
        if name in good_words:
            entities_score += entity_score
            total_entities_counted += 1
        elif name in bad_words:
            entities_score -= entity_score
            total_entities_counted += 1
    if total_entities_counted > 0:
        entities_score = entities_score / total_entities_counted
    if categories:
        for category in categories:
            if category.confidence > 0.5 and category.name in environment_categories:
                category_score += 2/3
                break
    sentiment_count = 0
    sentiment_score += sentiment.score
    for sentence in sentences:
        text = sentence.text.content.lower().translate(str.maketrans('', '', string.punctuation))
        good_count = 0
        bad_count = 0
        for phrase in good_words:
            if phrase in text:
                good_count += 1
        for phrase in bad_words:
            if phrase in text:
                bad_count += 1
        if good_count > 0 or bad_count > 0:
            sentiment_count += 1
            highlight_sentences[sentence.text.content] = ((good_count - bad_count) * sentence.sentiment.score) / (good_count + bad_count)
            sentiment_score += highlight_sentences[sentence.text.content]
    if sentiment_count > 0:
        sentiment_score = sentiment_score / sentiment_count
    if categories:
        total_score = entities_score * 0.4 + category_score * 0.3 + sentiment_score * 0.3
    else:
        total_score = entities_score * 0.7 + sentiment_score * 0.3
    return {"score": total_score, "highlighted": highlight_sentences}

def process_text(text): # Returns score from 0-100 representing sustainability
    type = language_v1.Document.Type.PLAIN_TEXT
    entities = analyze_entity_sentiment(text, type)
    try:
        categories = classify_text(text, type)
    except:
        categories = None
    sentiment, sentences = analyze_sentiment(text, type)
    return process(entities, categories, sentiment, sentences)

def process_html(html):
    type = language_v1.Document.Type.HTML
    entities = analyze_entity_sentiment(text, type)
    try:
        categories = classify_text(text, type)
    except:
        categories = None
    sentiment, sentences = analyze_sentiment(text, type)
    return process(entities, categories, sentiment, sentences)
