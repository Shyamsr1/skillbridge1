import json

import logging
logging.getLogger("transformers").setLevel(logging.ERROR)# Suppress transformers warnings


from transformers import pipeline

# Load zero-shot classifier from Hugging Face
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def identify_skill_gaps_dl(user_ratings, required_skills, job_role="Data Scientist", threshold=3, relevance_cutoff=0.6):
    """
    DL-based skill gap detection using zero-shot classification.

    Args:
        user_ratings (dict): Skill ratings from user.
        required_skills (list): Skills to evaluate.
        job_role (str): Target job role.
        threshold (int): Rating below which skill is a gap.
        relevance_cutoff (float): Minimum relevance to consider a gap.

    Returns:
        list of dicts: [{'skill': 'Python', 'rating': 2, 'relevance': 0.91}, ...]
    """
    result = classifier(sequences=required_skills, candidate_labels=[job_role])
    # relevance_scores = dict(zip(result["sequence"], result["scores"]))
    relevance_scores = {r["sequence"]: r["scores"][0] for r in result}
    
    # Filter skills based on user ratings and relevance
    gaps = []
    for skill in required_skills:
        rating = user_ratings.get(skill, 0)
        relevance = relevance_scores.get(skill, 0)
        if rating < threshold and relevance > relevance_cutoff:
            gaps.append({"skill": skill, "rating": rating, "relevance": round(relevance, 2)})
    return gaps
