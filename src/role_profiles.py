import re


COMPONENT_NAMES = [
    "Semantic Match",
    "Skill Alignment",
    "ATS Compatibility",
    "Resume Quality",
    "Experience / Project Evidence",
    "Model Confidence Signal",
]


def normalize_role_name(role: str) -> str:
    text = re.sub(r"\s+", " ", str(role or "").strip().lower())
    if not text:
        return "General / Unknown"

    role_patterns = [
        (
            "Generative AI Engineer",
            [r"\bgenerative ai engineer\b", r"\bgenai engineer\b", r"\bgen ai engineer\b", r"\bgenerative ai developer\b"],
        ),
        (
            "LLM Engineer",
            [r"\bllm engineer\b", r"\blarge language model engineer\b", r"\blanguage model engineer\b"],
        ),
        (
            "NLP Engineer",
            [r"\bnlp engineer\b", r"\bnatural language processing engineer\b"],
        ),
        (
            "Computer Vision Engineer",
            [r"\bcomputer vision engineer\b", r"\bcv engineer\b", r"\bvision engineer\b"],
        ),
        ("AI Engineer", [r"\bai engineer\b", r"\bartificial intelligence engineer\b"]),
        (
            "AI/ML Developer",
            [
                r"\bai/ml developer\b",
                r"\bai ml developer\b",
                r"\bai developer\b",
                r"\bmachine learning developer\b",
                r"\bml developer\b",
            ],
        ),
        ("Data Scientist", [r"\bdata scientist\b", r"\bdata science\b"]),
        ("MLOps Engineer", [r"\bmlops\b", r"\bmachine learning operations\b"]),
        ("ML Engineer", [r"\bml engineer\b", r"\bmachine learning engineer\b"]),
        (
            "Cloud/DevOps Engineer",
            [r"\bdevops engineer\b", r"\bdevops\b", r"\bcloud engineer\b", r"\bcloud/devops engineer\b", r"\bsite reliability\b", r"\bsre\b"],
        ),
        (
            "Software Developer",
            [r"\bsoftware developer\b", r"\bsoftware engineer\b", r"\bfrontend\b", r"\bbackend\b", r"\bfull stack\b"],
        ),
        ("Data Analyst", [r"\bdata analyst\b", r"\banalytics analyst\b", r"\bbi analyst\b"]),
        ("Business Analyst", [r"\bbusiness analyst\b", r"\bproduct analyst\b", r"\brequirements analyst\b"]),
    ]
    for normalized_role, patterns in role_patterns:
        if any(re.search(pattern, text) for pattern in patterns):
            return normalized_role
    return "General / Unknown"


def _profile(weights, categories, skills, guidance) -> dict:
    total_weight = round(sum(weights.values()), 6)
    if total_weight != 1.0:
        raise ValueError("Role profile component weights must sum to 1.0.")
    return {
        "component_weights": weights,
        "priority_skill_categories": categories,
        "priority_skills": skills,
        "role_guidance": guidance,
    }


def get_role_profiles() -> dict:
    return {
        "General / Unknown": _profile(
            {
                "Semantic Match": 0.25,
                "Skill Alignment": 0.25,
                "ATS Compatibility": 0.20,
                "Resume Quality": 0.15,
                "Experience / Project Evidence": 0.10,
                "Model Confidence Signal": 0.05,
            },
            ["Programming", "Data Analysis", "Tools", "Soft Skills"],
            ["Python", "SQL", "Communication", "Problem Solving"],
            "Use the general profile when the target role is unclear or broad.",
        ),
        "Data Scientist": _profile(
            {
                "Semantic Match": 0.25,
                "Skill Alignment": 0.30,
                "ATS Compatibility": 0.15,
                "Resume Quality": 0.10,
                "Experience / Project Evidence": 0.15,
                "Model Confidence Signal": 0.05,
            },
            ["Programming", "Data Analysis", "Machine Learning", "Statistics", "Visualization", "Databases"],
            ["Python", "SQL", "Pandas", "Scikit-learn", "Statistics", "Machine Learning"],
            "Prioritize ML, statistics, data analysis, and measurable project evidence.",
        ),
        "ML Engineer": _profile(
            {
                "Semantic Match": 0.25,
                "Skill Alignment": 0.30,
                "ATS Compatibility": 0.15,
                "Resume Quality": 0.10,
                "Experience / Project Evidence": 0.15,
                "Model Confidence Signal": 0.05,
            },
            ["Programming", "Machine Learning", "Deep Learning", "MLOps", "Cloud", "Backend/API"],
            ["Python", "PyTorch", "TensorFlow", "APIs", "Docker", "Cloud"],
            "Prioritize production ML skills, engineering depth, deployment evidence, and APIs.",
        ),
        "AI Engineer": _profile(
            {
                "Semantic Match": 0.25,
                "Skill Alignment": 0.30,
                "ATS Compatibility": 0.15,
                "Resume Quality": 0.10,
                "Experience / Project Evidence": 0.15,
                "Model Confidence Signal": 0.05,
            },
            ["Programming", "Machine Learning", "Deep Learning", "NLP", "Backend/API", "Cloud", "MLOps"],
            [
                "python",
                "machine learning",
                "deep learning",
                "tensorflow",
                "pytorch",
                "fastapi",
                "docker",
                "cloud",
                "api",
                "model deployment",
            ],
            "AI Engineer profiles prioritize applied AI development, model integration, APIs, deployment readiness, and production-oriented project evidence.",
        ),
        "AI/ML Developer": _profile(
            {
                "Semantic Match": 0.25,
                "Skill Alignment": 0.30,
                "ATS Compatibility": 0.15,
                "Resume Quality": 0.10,
                "Experience / Project Evidence": 0.15,
                "Model Confidence Signal": 0.05,
            },
            ["Programming", "Machine Learning", "Deep Learning", "Backend/API", "Tools", "Cloud", "MLOps"],
            [
                "python",
                "scikit-learn",
                "tensorflow",
                "pytorch",
                "fastapi",
                "flask",
                "git",
                "docker",
                "sql",
                "model deployment",
            ],
            "AI/ML Developer profiles prioritize practical model development, Python engineering, APIs, and deployable AI applications.",
        ),
        "Generative AI Engineer": _profile(
            {
                "Semantic Match": 0.30,
                "Skill Alignment": 0.30,
                "ATS Compatibility": 0.10,
                "Resume Quality": 0.10,
                "Experience / Project Evidence": 0.15,
                "Model Confidence Signal": 0.05,
            },
            ["NLP", "Generative AI", "LLMs", "Vector Databases", "Backend/API", "Cloud", "MLOps", "Programming"],
            [
                "generative ai",
                "genai",
                "llm",
                "large language models",
                "rag",
                "retrieval augmented generation",
                "embeddings",
                "vector database",
                "langchain",
                "llamaindex",
                "prompt engineering",
                "openai api",
                "hugging face",
                "fastapi",
                "python",
            ],
            "Generative AI Engineer profiles prioritize LLM applications, RAG pipelines, embeddings, vector search, prompt engineering, and production API integration.",
        ),
        "LLM Engineer": _profile(
            {
                "Semantic Match": 0.30,
                "Skill Alignment": 0.30,
                "ATS Compatibility": 0.10,
                "Resume Quality": 0.10,
                "Experience / Project Evidence": 0.15,
                "Model Confidence Signal": 0.05,
            },
            ["LLMs", "NLP", "Generative AI", "Vector Databases", "Backend/API", "MLOps", "Cloud", "Programming"],
            [
                "llm",
                "large language models",
                "transformers",
                "bert",
                "gpt",
                "rag",
                "embeddings",
                "vector database",
                "faiss",
                "chromadb",
                "langchain",
                "llamaindex",
                "hugging face",
                "fine-tuning",
                "prompt engineering",
                "python",
            ],
            "LLM Engineer profiles prioritize language model systems, retrieval pipelines, embeddings, evaluation, fine-tuning awareness, and scalable API integration.",
        ),
        "NLP Engineer": _profile(
            {
                "Semantic Match": 0.30,
                "Skill Alignment": 0.30,
                "ATS Compatibility": 0.10,
                "Resume Quality": 0.10,
                "Experience / Project Evidence": 0.15,
                "Model Confidence Signal": 0.05,
            },
            ["NLP", "Machine Learning", "Deep Learning", "Programming", "Data Analysis", "MLOps"],
            [
                "nlp",
                "natural language processing",
                "text classification",
                "sentiment analysis",
                "tokenization",
                "transformers",
                "bert",
                "word2vec",
                "tf-idf",
                "nltk",
                "spacy",
                "hugging face",
                "python",
                "pytorch",
                "tensorflow",
            ],
            "NLP Engineer profiles prioritize text processing, language models, NLP pipelines, model evaluation, and applied text intelligence projects.",
        ),
        "Computer Vision Engineer": _profile(
            {
                "Semantic Match": 0.25,
                "Skill Alignment": 0.30,
                "ATS Compatibility": 0.10,
                "Resume Quality": 0.10,
                "Experience / Project Evidence": 0.20,
                "Model Confidence Signal": 0.05,
            },
            ["Computer Vision", "Deep Learning", "Programming", "Machine Learning", "MLOps", "Cloud"],
            [
                "computer vision",
                "opencv",
                "image processing",
                "object detection",
                "image classification",
                "cnn",
                "yolo",
                "pytorch",
                "tensorflow",
                "python",
                "model evaluation",
                "model deployment",
            ],
            "Computer Vision Engineer profiles prioritize image/video understanding, deep learning, OpenCV, object detection, model evaluation, and deployable CV projects.",
        ),
        "MLOps Engineer": _profile(
            {
                "Semantic Match": 0.20,
                "Skill Alignment": 0.35,
                "ATS Compatibility": 0.15,
                "Resume Quality": 0.10,
                "Experience / Project Evidence": 0.15,
                "Model Confidence Signal": 0.05,
            },
            ["MLOps", "Cloud", "Backend/API", "Programming", "Databases", "Tools"],
            ["Docker", "Kubernetes", "CI/CD", "MLflow", "Cloud", "APIs"],
            "Prioritize deployment, automation, monitoring, cloud, and ML pipeline evidence.",
        ),
        "Software Developer": _profile(
            {
                "Semantic Match": 0.20,
                "Skill Alignment": 0.30,
                "ATS Compatibility": 0.15,
                "Resume Quality": 0.15,
                "Experience / Project Evidence": 0.15,
                "Model Confidence Signal": 0.05,
            },
            ["Programming", "Backend/API", "Databases", "Tools", "Cloud"],
            ["Python", "JavaScript", "APIs", "SQL", "Git", "Testing"],
            "Prioritize programming, project evidence, APIs, databases, and readable engineering bullets.",
        ),
        "Data Analyst": _profile(
            {
                "Semantic Match": 0.20,
                "Skill Alignment": 0.30,
                "ATS Compatibility": 0.20,
                "Resume Quality": 0.15,
                "Experience / Project Evidence": 0.10,
                "Model Confidence Signal": 0.05,
            },
            ["Data Analysis", "Databases", "Visualization", "Statistics", "Soft Skills"],
            ["SQL", "Excel", "Tableau", "Power BI", "Statistics", "Communication"],
            "Prioritize SQL, dashboards, analysis, reporting clarity, and business-facing impact.",
        ),
        "Business Analyst": _profile(
            {
                "Semantic Match": 0.25,
                "Skill Alignment": 0.20,
                "ATS Compatibility": 0.20,
                "Resume Quality": 0.20,
                "Experience / Project Evidence": 0.10,
                "Model Confidence Signal": 0.05,
            },
            ["Data Analysis", "Visualization", "Soft Skills", "Domain Knowledge", "Databases"],
            ["Requirements", "SQL", "Excel", "Dashboards", "Stakeholder Communication", "Documentation"],
            "Prioritize business context, clear communication, requirements, analysis, and stakeholder impact.",
        ),
        "Cloud/DevOps Engineer": _profile(
            {
                "Semantic Match": 0.20,
                "Skill Alignment": 0.35,
                "ATS Compatibility": 0.15,
                "Resume Quality": 0.10,
                "Experience / Project Evidence": 0.15,
                "Model Confidence Signal": 0.05,
            },
            ["Cloud", "MLOps", "Tools", "Backend/API", "Databases"],
            ["AWS", "Azure", "Docker", "Kubernetes", "CI/CD", "Terraform"],
            "Prioritize cloud platforms, automation, deployment, infrastructure, and operational evidence.",
        ),
    }


def get_role_profile(role: str) -> dict:
    profiles = get_role_profiles()
    target_role = normalize_role_name(role)
    profile = profiles.get(target_role) or profiles["General / Unknown"]
    return {"target_role": target_role, **profile}


def infer_target_role(predicted_role=None, job_description: str = "") -> str:
    jd_text = str(job_description or "").lower()
    llm_exact_terms = [
        "llm engineer",
        "large language model engineer",
        "language model engineer",
    ]
    genai_terms = [
        "generative ai",
        "genai",
        "gen ai",
        "rag",
        "retrieval augmented generation",
        "prompt engineering",
        "llm",
        "large language model",
        "langchain",
        "llamaindex",
        "vector database",
        "embeddings",
    ]
    if any(term in jd_text for term in llm_exact_terms):
        return "LLM Engineer"
    if any(term in jd_text for term in genai_terms):
        return "Generative AI Engineer"

    nlp_terms = [
        "nlp engineer",
        "natural language processing",
        "text classification",
        "sentiment analysis",
        "tokenization",
        "spacy",
        "nltk",
    ]
    if any(term in jd_text for term in nlp_terms):
        return "NLP Engineer"

    computer_vision_terms = [
        "computer vision",
        "opencv",
        "image processing",
        "object detection",
        "image classification",
        "yolo",
    ]
    if any(term in jd_text for term in computer_vision_terms):
        return "Computer Vision Engineer"

    ai_engineer_terms = [
        "ai engineer",
        "artificial intelligence engineer",
    ]
    if any(term in jd_text for term in ai_engineer_terms):
        return "AI Engineer"

    ai_ml_developer_terms = [
        "ai/ml developer",
        "ai ml developer",
        "ai developer",
        "ml developer",
        "machine learning developer",
    ]
    if any(term in jd_text for term in ai_ml_developer_terms):
        return "AI/ML Developer"

    existing_role_checks = [
        ("Data Scientist", ["data scientist", "data science"]),
        ("MLOps Engineer", ["mlops", "machine learning operations"]),
        ("ML Engineer", ["ml engineer", "machine learning engineer"]),
        ("Software Developer", ["software developer", "software engineer", "frontend", "backend", "full stack"]),
        ("Data Analyst", ["data analyst", "analytics analyst", "bi analyst"]),
        ("Business Analyst", ["business analyst", "product analyst", "requirements analyst"]),
        ("Cloud/DevOps Engineer", ["devops engineer", "devops", "cloud engineer", "cloud/devops engineer"]),
    ]
    for role, terms in existing_role_checks:
        if any(term in jd_text for term in terms):
            return role

    predicted = normalize_role_name(predicted_role)
    if predicted != "General / Unknown":
        return predicted
    return "General / Unknown"


def get_role_profile_summary(role_profile: dict) -> dict:
    role_profile = role_profile if isinstance(role_profile, dict) else get_role_profile("General / Unknown")
    weights = role_profile.get("component_weights", {}) or {}
    top_component = "Not available"
    if weights:
        top_component = max(weights, key=weights.get)

    return {
        "target_role": role_profile.get("target_role", "General / Unknown"),
        "top_weighted_component": top_component,
        "priority_categories": role_profile.get("priority_skill_categories", []) or [],
        "role_guidance": role_profile.get("role_guidance", ""),
    }
