import json

# Updated multilingual translator using deep-translator and Hugging Face transformers

from deep_translator import GoogleTranslator
import logging
logging.getLogger("transformers").setLevel(logging.ERROR)# Suppress transformers warnings

from transformers import MarianMTModel, MarianTokenizer

# UI dictionary remains available
translations = {
    "en": {"welcome": "Welcome", "start": "Start", "exit": "Exit"},
    "fr": {"welcome": "Bienvenue", "start": "Démarrer", "exit": "Quitter"},
    "ta": {"welcome": "வணக்கம்", "start": "தொடங்கு", "exit": "வெளியேறு"},
    "hi": {"welcome": "स्वागत है", "start": "शुरू करें", "exit": "बाहर जाएं"},
    "es": {"welcome": "Bienvenido", "start": "Comenzar", "exit": "Salir"}
}

# --- Google Translate API ---
def translate_text(text, target_lang="fr", source_lang="auto"):
    try:
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    except Exception as e:
        return f"[Translation Error]: {e}"

# --- Deep Learning-based Translation using MarianMT ---
def translate_text_dl(text, source_lang="en", target_lang="fr"):
    try:
        model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name)

        tokenized = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        translated = model.generate(**tokenized)
        output = tokenizer.decode(translated[0], skip_special_tokens=True)
        return output
    except Exception as e:
        return f"[DL Translation Error]: {e}"

# --- Smart Wrapper to Choose Method ---
def smart_translate(text, target_lang="fr", source_lang="en", method="google"):
    if method == "dl":
        return translate_text_dl(text, source_lang, target_lang)
    else:
        return translate_text(text, target_lang, source_lang)
