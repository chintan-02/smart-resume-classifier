import re


TAXONOMY_ORDER = [
    "Programming",
    "Data Analysis",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "Generative AI",
    "LLMs",
    "Vector Databases",
    "Computer Vision",
    "MLOps",
    "Cloud",
    "Databases",
    "Backend/API",
    "Visualization",
    "Tools",
    "Statistics",
    "Soft Skills",
    "Domain Knowledge",
    "Other",
]


def normalize_skill(skill: str) -> str:
    text = str(skill or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def get_skill_taxonomy() -> dict:
    return {
        "Programming": [
            "python",
            "java",
            "javascript",
            "typescript",
            "c++",
            "c",
            "r",
            "sql",
            "bash",
        ],
        "Data Analysis": [
            "pandas",
            "numpy",
            "excel",
            "data cleaning",
            "data analysis",
            "exploratory data analysis",
            "eda",
        ],
        "Machine Learning": [
            "machine learning",
            "scikit-learn",
            "sklearn",
            "xgboost",
            "lightgbm",
            "random forest",
            "logistic regression",
            "classification",
            "regression",
            "clustering",
            "feature engineering",
            "model evaluation",
        ],
        "Deep Learning": [
            "deep learning",
            "tensorflow",
            "pytorch",
            "keras",
            "neural networks",
            "cnn",
            "rnn",
            "transformers",
        ],
        "NLP": [
            "nlp",
            "natural language processing",
            "text classification",
            "sentiment analysis",
            "bert",
            "word2vec",
            "tf-idf",
            "tokenization",
            "nltk",
            "spacy",
        ],
        "Generative AI": [
            "generative ai",
            "genai",
            "prompt engineering",
            "openai api",
            "ai agents",
            "rag",
            "retrieval augmented generation",
        ],
        "LLMs": [
            "llm",
            "large language models",
            "transformers",
            "gpt",
            "bert",
            "hugging face",
            "fine-tuning",
            "embeddings",
        ],
        "Vector Databases": [
            "vector database",
            "faiss",
            "chromadb",
            "pinecone",
            "weaviate",
            "qdrant",
        ],
        "Computer Vision": [
            "computer vision",
            "opencv",
            "image processing",
            "object detection",
            "cnn",
            "yolo",
        ],
        "MLOps": [
            "mlops",
            "docker",
            "kubernetes",
            "k8s",
            "mlflow",
            "ci/cd",
            "github actions",
            "model monitoring",
            "experiment tracking",
        ],
        "Cloud": [
            "aws",
            "azure",
            "gcp",
            "google cloud",
            "azure app service",
            "sagemaker",
        ],
        "Databases": [
            "sql",
            "mysql",
            "postgresql",
            "sqlite",
            "mongodb",
            "database",
            "data warehouse",
        ],
        "Backend/API": [
            "fastapi",
            "flask",
            "rest api",
            "api",
            "pydantic",
            "backend",
        ],
        "Visualization": [
            "tableau",
            "power bi",
            "matplotlib",
            "seaborn",
            "plotly",
            "data visualization",
            "dashboard",
            "streamlit",
        ],
        "Tools": [
            "git",
            "github",
            "jupyter",
            "vscode",
            "postman",
            "linux",
        ],
        "Statistics": [
            "statistics",
            "probability",
            "hypothesis testing",
            "regression analysis",
            "a/b testing",
        ],
        "Soft Skills": [
            "communication",
            "teamwork",
            "leadership",
            "problem solving",
            "stakeholder",
            "collaboration",
        ],
        "Domain Knowledge": [
            "healthcare",
            "finance",
            "supply chain",
            "retail",
            "education",
        ],
        "Other": [],
    }


def _coerce_skills(skills) -> list[str]:
    if skills is None:
        return []
    if isinstance(skills, str):
        return [skill.strip() for skill in skills.split(",") if skill.strip()]
    if isinstance(skills, (list, set, tuple)):
        return [str(skill).strip() for skill in skills if str(skill).strip()]
    return []


def _readable_skill(skill: str) -> str:
    normalized = normalize_skill(skill)
    readable_overrides = {
        "api": "API",
        "aws": "AWS",
        "azure": "Azure",
        "c++": "C++",
        "ci/cd": "CI/CD",
        "cnn": "CNN",
        "chromadb": "ChromaDB",
        "eda": "EDA",
        "faiss": "FAISS",
        "gcp": "GCP",
        "generative ai": "Generative AI",
        "genai": "GenAI",
        "gpt": "GPT",
        "github": "GitHub",
        "hugging face": "Hugging Face",
        "llm": "LLM",
        "large language models": "Large Language Models",
        "html": "HTML",
        "k8s": "K8s",
        "kubernetes": "Kubernetes",
        "mlflow": "MLflow",
        "mlops": "MLOps",
        "nlp": "NLP",
        "numpy": "NumPy",
        "opencv": "OpenCV",
        "openai api": "OpenAI API",
        "pandas": "Pandas",
        "pinecone": "Pinecone",
        "power bi": "Power BI",
        "pytorch": "PyTorch",
        "qdrant": "Qdrant",
        "rnn": "RNN",
        "sql": "SQL",
        "tf-idf": "TF-IDF",
        "weaviate": "Weaviate",
        "vscode": "VS Code",
        "yolo": "YOLO",
    }
    return readable_overrides.get(normalized, normalized.title())


def categorize_skills(skills) -> dict:
    taxonomy = get_skill_taxonomy()
    category_lookup = {}
    for category in TAXONOMY_ORDER:
        for skill in taxonomy.get(category, []):
            normalized = normalize_skill(skill)
            if normalized not in category_lookup:
                category_lookup[normalized] = category

    categorized = {category: [] for category in TAXONOMY_ORDER}
    seen = set()
    for skill in _coerce_skills(skills):
        normalized = normalize_skill(skill)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        category = category_lookup.get(normalized, "Other")
        categorized[category].append(_readable_skill(normalized))

    return {category: values for category, values in categorized.items() if values}


def _category_count(categories: dict, category: str) -> int:
    return len((categories or {}).get(category, []))


def _coverage_status(resume_count: int, matched_count: int, missing_count: int) -> str:
    if matched_count > 0 and missing_count == 0:
        return "Strong"
    if matched_count > missing_count:
        return "Good"
    if matched_count > 0 and missing_count > 0:
        return "Partial"
    if missing_count > 0 and matched_count == 0:
        return "Gap"
    if resume_count > 0:
        return "Resume Only"
    return "Not Detected"


def compare_skill_categories(
    resume_skills=None,
    jd_skills=None,
    matched_skills=None,
    missing_skills=None,
    extra_skills=None,
) -> dict:
    resume_categories = categorize_skills(resume_skills)
    jd_categories = categorize_skills(jd_skills)
    matched_categories = categorize_skills(matched_skills)
    missing_categories = categorize_skills(missing_skills)
    extra_categories = categorize_skills(extra_skills)

    category_summary = []
    for category in TAXONOMY_ORDER:
        resume_count = _category_count(resume_categories, category)
        jd_count = _category_count(jd_categories, category)
        matched_count = _category_count(matched_categories, category)
        missing_count = _category_count(missing_categories, category)
        extra_count = _category_count(extra_categories, category)
        if not any([resume_count, jd_count, matched_count, missing_count, extra_count]):
            continue

        category_summary.append(
            {
                "category": category,
                "resume_count": resume_count,
                "jd_count": jd_count,
                "matched_count": matched_count,
                "missing_count": missing_count,
                "extra_count": extra_count,
                "coverage_status": _coverage_status(resume_count, matched_count, missing_count),
            }
        )

    top_strength_categories = [
        item["category"]
        for item in sorted(
            category_summary,
            key=lambda value: (value["matched_count"], value["resume_count"]),
            reverse=True,
        )
        if item["matched_count"] > 0
    ][:3]
    top_gap_categories = [
        item["category"]
        for item in sorted(
            category_summary,
            key=lambda value: value["missing_count"],
            reverse=True,
        )
        if item["missing_count"] > 0
    ][:3]

    return {
        "resume_categories": resume_categories,
        "jd_categories": jd_categories,
        "matched_categories": matched_categories,
        "missing_categories": missing_categories,
        "extra_categories": extra_categories,
        "category_summary": category_summary,
        "top_strength_categories": top_strength_categories,
        "top_gap_categories": top_gap_categories,
    }


def get_skill_taxonomy_summary(taxonomy_result: dict) -> dict:
    taxonomy_result = taxonomy_result if isinstance(taxonomy_result, dict) else {}
    resume_categories = taxonomy_result.get("resume_categories", {}) or {}
    missing_categories = taxonomy_result.get("missing_categories", {}) or {}
    top_strength_categories = taxonomy_result.get("top_strength_categories", []) or []
    top_gap_categories = taxonomy_result.get("top_gap_categories", []) or []

    total_resume_categories = len(resume_categories)
    total_gap_categories = len(missing_categories)
    if top_strength_categories:
        top_strength_message = "Strongest detected categories: " + ", ".join(top_strength_categories) + "."
    else:
        top_strength_message = "No matched strength categories detected yet."

    if top_gap_categories:
        top_gap_message = (
            "Category-level gaps detected in "
            + ", ".join(top_gap_categories)
            + ". Add missing skills only if they reflect your real experience."
        )
    else:
        top_gap_message = "No category-level gaps detected from the current job description."

    return {
        "total_resume_categories": total_resume_categories,
        "total_gap_categories": total_gap_categories,
        "top_strength_message": top_strength_message,
        "top_gap_message": top_gap_message,
    }
