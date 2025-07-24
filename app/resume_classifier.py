import json
import logging
logging.getLogger("transformers").setLevel(logging.ERROR)# Suppress transformers warnings

from transformers import pipeline

classifier = pipeline("text-classification", model="bhadresh-savani/bert-base-uncased-emotion")

def classify_resume(text):
    return classifier(text[:512])

