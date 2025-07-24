import json

from langdetect import detect
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
# from . import parser
from app import resume_parser_dl as parser
# Load DL language detection model
model_name = "papluca/xlm-roberta-base-language-detection"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Map label index to language code
id2label = model.config.id2label

# Deep Learning-based language detection
def detect_language_dl(text):
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = model(**inputs).logits
            probs = F.softmax(logits, dim=-1)
            predicted_id = torch.argmax(probs, dim=1).item()
            return id2label[predicted_id]
    except Exception as e:
        print("DL Language detection error:", e)
        return "unknown"

# Choose detection method: 'langdetect' or 'dl'
def detect_resume_language(resume_path, method="langdetect"):
    try:
        text = parser.extract_text_from_pdf(resume_path)
        if method == "dl":
            return detect_language_dl(text)
        else:
            return detect(text)
    except Exception as e:
        print("Language detection error:", e)
        return "unknown"

def parse_resume_with_language(resume_path, skill_list=None, method="langdetect"):
    parsed_data = parser.parse_resume(resume_path)
    parsed_data["DetectedLanguage"] = detect_resume_language(resume_path, method=method)
    return parsed_data
