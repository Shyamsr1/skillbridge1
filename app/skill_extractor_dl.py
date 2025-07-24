import re
from sentence_transformers import SentenceTransformer, util
import json

# Load semantic model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 🔧 FIXED Semantic Skill Extractor
def load_alias_map(skill_master_path="data/skill_master.json", return_aliases=False):
    with open(skill_master_path, "r", encoding="utf-8") as f:
        skill_master = json.load(f)

    alias_map = {}
    all_aliases = []

    for canonical, meta in skill_master["skills"].items():
        alias_map[canonical.lower()] = canonical
        all_aliases.append(canonical)
        for alias in meta.get("alias", []):
            alias_map[alias.lower()] = canonical
            all_aliases.append(alias)

    return (alias_map, all_aliases) if return_aliases else alias_map

# adjust threshold for cosine similarity for more words to extract from resume
def extract_skills_dl(text, skill_list, threshold=0.2, skill_master_path="data/skill_master.json"): 
    sentences = re.split(r'[\.\!?]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]

    alias_map, all_aliases = load_alias_map(skill_master_path, return_aliases=True)
    skill_embeddings = model.encode(all_aliases, convert_to_tensor=True)
    extracted = set()

    for sentence in sentences:
        sentence_embedding = model.encode(sentence, convert_to_tensor=True)
        cos_scores = util.pytorch_cos_sim(sentence_embedding, skill_embeddings)[0]
        for i, score in enumerate(cos_scores):
            if score.item() >= threshold:
                matched_alias = all_aliases[i]
                canonical = alias_map.get(matched_alias.lower(), matched_alias)
                extracted.add(canonical)

    return sorted(list(extracted))

# --- Enhanced: Job Role Detection using unified skill_master.json ---
def detect_job_role(text, skill_master_path="data/skill_master.json"):
    """Predict the most likely job role from resume text using roles and aliases."""
    import json
    with open(skill_master_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    alias_map = data.get("role_aliases", {})
    roles = list(data.get("roles", {}).keys())
    canonical_roles = roles.copy()

    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer("all-MiniLM-L6-v2")

    role_embeddings = model.encode(roles, convert_to_tensor=True)
    text_embedding = model.encode(text, convert_to_tensor=True)

    scores = util.pytorch_cos_sim(text_embedding, role_embeddings)[0]
    best_idx = scores.argmax().item()

    return canonical_roles[best_idx]