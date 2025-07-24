
import json
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

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

# This function extracts skills from a given text using a pre-trained model 
# and a threshold =0.95 for cosine similarity.
# It returns a sorted list of extracted skills.  
def extract_skills_dl_v2(text, threshold=0.95, skill_master_path="data/skill_master.json"):
    alias_map, all_aliases = load_alias_map(skill_master_path, return_aliases=True)
    resume_embedding = model.encode(text, convert_to_tensor=True)
    skill_embeddings = model.encode(all_aliases, convert_to_tensor=True)

    cos_scores = util.pytorch_cos_sim(resume_embedding, skill_embeddings)[0]

    extracted = set()
    for i, score in enumerate(cos_scores):
        if score.item() >= threshold:
            matched_alias = all_aliases[i]
            canonical = alias_map.get(matched_alias.lower(), matched_alias)
            extracted.add(canonical)

    return sorted(list(extracted))
