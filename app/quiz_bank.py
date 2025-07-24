
# quiz_bank.py
import json, os

# Adjust path as needed (relative to where Streamlit runs)
json_path = os.path.join("data", "quiz_bank.json")

with open(json_path, "r", encoding="utf-8") as f:
    quiz_bank = json.load(f)


def get_question_by_topic(topic):
    try:
        return quiz_bank[topic]["basic"] + quiz_bank[topic]["intermediate"] + quiz_bank[topic]["advanced"]
    except KeyError:
        return []

def get_question_by_difficulty(topic, difficulty):
    try:
        return quiz_bank[topic][difficulty]
    except KeyError:
        return []
