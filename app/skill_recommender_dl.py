import json

from sentence_transformers import SentenceTransformer, util

# Use a powerful DL model for semantic comparison
model = SentenceTransformer('all-mpnet-base-v2')  # More accurate than MiniLM

# --- Semantic Skill Recommender with Confidence Scores ---
def recommend_skills(user_skills, skill_corpus, top_k=5):
    user_vecs = model.encode(user_skills, convert_to_tensor=True)
    corpus_vecs = model.encode(skill_corpus, convert_to_tensor=True)
    scores = util.pytorch_cos_sim(user_vecs, corpus_vecs)
    top_matches = scores.topk(top_k, dim=1)
    return [(skill_corpus[i], round(scores[0][i].item(), 3)) for i in top_matches.indices[0]]

# --- Personalized Missing Skill Recommender for Job Role ---
def recommend_missing_skills(user_skills, job_role_skills, top_k=5):
    missing_skills = list(set(job_role_skills) - set(user_skills))
    return recommend_skills(user_skills, missing_skills, top_k=top_k)

# --- Learning Path Recommendations ---

def recommend_learning_paths(skill_ratings, resume_skills=None, quiz_scores=None, threshold=4):
    learning_resources = {
        "Python": "https://www.learnpython.org/",
        "SQL": "https://www.sqltutorial.org/",
        "Machine Learning": "https://developers.google.com/machine-learning/crash-course",
        "Power BI": "https://learn.microsoft.com/en-us/power-bi/",
        "Communication": "https://www.youtube.com/@EnglishSpeakingCourses",
        "Deep Learning": "https://www.geeksforgeeks.org/deep-learning/introduction-deep-learning/"
    }

    recommendations = []

    for skill, rating in skill_ratings.items():
        rating_score = rating
        resume_score = 1 if resume_skills and skill.lower() in [s.lower() for s in resume_skills] else 0
        quiz_score = quiz_scores.get(skill, 0) if quiz_scores else 0

        # Calculate readiness out of 6 (5+1), weight rating + resume
        readiness = rating_score + resume_score

        if readiness < threshold or quiz_score < 3:  # weak skill or low quiz
            resource = learning_resources.get(skill)
            if resource:
                recommendations.append((skill, resource))

    return recommendations


