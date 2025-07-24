
import fitz  # PyMuPDF
import re
import json
import spacy
from sentence_transformers import SentenceTransformer, util
import logging
logging.getLogger("transformers").setLevel(logging.ERROR) #Suppress transformers warnings 

from transformers import pipeline
from keybert import KeyBERT
from sklearn.cluster import KMeans

# Load models
nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")
kw_model = KeyBERT()
ner_pipe = pipeline("ner", model="dslim/bert-base-NER")
summarizer = pipeline("summarization")

# --- Basic Text Extraction ---
def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# --- Load Skill List from JSON ---
def load_skill_list(json_path="data/skill_master.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        skills_data = json.load(f)

    skill_list = []
    for skill, meta in skills_data.items():
        skill_list.append(skill)
        if "alias" in meta:  # use 'alias' (not 'aliases') consistently
            skill_list.extend(meta["alias"])

    return list(set(skill_list)) # removes duplicates



# --- Regex-based Skill Extraction ---
def extract_skills(text, skill_list):
    text = text.lower()
    skill_list_normalized = [skill.lower() for skill in skill_list]
    extracted = []
    for skill in skill_list_normalized:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text):
            extracted.append(skill.title())
    return extracted

# --- DL-based Semantic Skill Extraction ---
def extract_skills_dl(text, skill_list, threshold=0.75):
    sentences = re.split(r'[\n\r\.!?]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
    extracted = set()
    skill_embeddings = model.encode(skill_list, convert_to_tensor=True)

    for sentence in sentences:
        sentence_embedding = model.encode(sentence, convert_to_tensor=True)
        cos_scores = util.pytorch_cos_sim(sentence_embedding, skill_embeddings)[0]
        for i, score in enumerate(cos_scores):
            if score.item() >= threshold:
                extracted.add(skill_list[i])
    return list(extracted)

# --- spaCy Named Entity Skills ---
def extract_skills_spacy(text):
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ in ["ORG", "SKILL", "WORK_OF_ART", "PRODUCT"]]

# --- BERT-based NER Skills ---
def extract_skills_bert(text):
    entities = ner_pipe(text)
    return [e['word'] for e in entities if e['entity'].startswith('B-')]

# --- Semantic Matching of Extracted to Known Skills ---
def semantic_match_skills(extracted, known_skills):
    matches = []
    for skill in extracted:
        emb1 = model.encode(skill, convert_to_tensor=True)
        for target in known_skills:
            emb2 = model.encode(target, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(emb1, emb2)
            if similarity.item() > 0.75:
                matches.append(target)
    return list(set(matches))

# --- Keyword Extraction ---
def extract_keywords(text, top_n=10):
    return [kw[0] for kw in kw_model.extract_keywords(text, stop_words='english', top_n=top_n)]

# --- Text Summarization ---
def generate_summary(text):
    if len(text) < 100:
        return text
    return summarizer(text[:1000], max_length=100, min_length=30, do_sample=False)[0]['summary_text']

# --- Resume Clustering ---
def cluster_resumes(resume_embeddings, n_clusters=5):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    return kmeans.fit_predict(resume_embeddings)

# --- Unified Resume Parser with Full NLP + DL ---
def parse_resume_unified(file_path, threshold=0.75):
    skill_list = load_skill_list()
    text = extract_text_from_pdf(file_path)

    email = re.search(r"[\w\.-]+@[\w\.-]+", text)
    phone = re.search(r"(\+91[-\s]?)?[0]?[6789]\d{9}", text)

    skills_regex = extract_skills(text, skill_list)
    skills_dl = extract_skills_dl(text, skill_list, threshold)
    skills_spacy = extract_skills_spacy(text)
    skills_bert = extract_skills_bert(text)
    semantic_skills = semantic_match_skills(skills_spacy, skill_list)
    summary = generate_summary(text)
    keywords = extract_keywords(text)

    return {
        "Email": email.group() if email else "",
        "Phone": phone.group() if phone else "",
        "Skills_Regex": skills_regex,
        "Skills_DL": skills_dl,
        "Skills_SpaCy": skills_spacy,
        "Skills_BERT": skills_bert,
        "Skills_Semantic": semantic_skills,
        "Summary": summary,
        "Keywords": keywords
    }
