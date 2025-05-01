import streamlit as st
import fitz  # PyMuPDF
import re
import tempfile
import os

st.set_page_config(page_title="FAANG ATS Simulator", layout="wide")

# --- FAANG Keyword Maps ---
FAANG_CRITERIA = {
    "Meta": {
        "keywords": [
            "React.js", "GraphQL", "JavaScript", "Python", "PHP", "Hack",
            "microservices", "scalable systems", "engagement", "feed ranking",
            "load balancing", "developer tooling", "mentored", "collaborated", "production issues"
        ],
        "focus": "System design, impact metrics, scalable systems, team leadership"
    },
    "Amazon": {
        "keywords": [
            "AWS", "DynamoDB", "Lambda", "S3", "EC2", "serverless", "Agile",
            "ownership", "customer obsession", "automated", "latency", "deployment", "high-traffic"
        ],
        "focus": "Leadership principles, AWS stack, measurable results, scalability"
    },
    "Apple": {
        "keywords": [
            "Swift", "Objective-C", "Xcode", "iOS", "macOS", "Unix", "CI/CD", "debugged", "hybrid apps",
            "reusable components", "design verification", "load balancing", "communication"
        ],
        "focus": "UX, Apple ecosystem, hardware/software integration, reusable code"
    },
    "Netflix": {
        "keywords": [
            "AWS", "Kubernetes", "microservices", "streaming", "buffering", "personalization",
            "A/B testing", "automation", "monitoring", "alerting", "fast-paced", "data-driven"
        ],
        "focus": "Scalable backend, streaming optimization, rapid deployment, data-first thinking"
    },
    "Google": {
        "keywords": [
            "Python", "C++", "Java", "Go", "MapReduce", "distributed systems", "search accuracy",
            "TensorFlow", "BigQuery", "mentored", "CI/CD", "RESTful APIs", "privacy"
        ],
        "focus": "Algorithms, distributed systems, ML, research collaboration"
    }
}

# --- Scoring Logic ---
def score_resume(text, keywords):
    score = 0
    for word in keywords:
        if word.lower() in text.lower():
            score += 5
    quantified = re.findall(r'\d+%|\$\d+|[0-9]+ users?', text)
    score += len(quantified) * 3
    action_verbs = ["implemented", "designed", "optimized", "deployed", "collaborated", "led", "automated"]
    score += sum(text.lower().count(v) for v in action_verbs)
    return min(score, 100)

# --- Streamlit UI ---
st.title("🎯 FAANG Resume Evaluator")

uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    doc = fitz.open(tmp_path)
    resume_text = "\n".join([page.get_text() for page in doc])
    os.remove(tmp_path)

    st.subheader("📄 Resume Text Preview")
    st.text_area("Extracted Resume Text", resume_text, height=300)

    st.subheader("📊 ATS Scores by Company")

    score_table = []

    for company, data in FAANG_CRITERIA.items():
        score = score_resume(resume_text, data["keywords"])
        verdict = "✅ Likely to Pass ATS" if score >= 70 else "⚠️ Borderline" if score >= 50 else "❌ Unlikely"
        score_table.append((company, score, verdict, data["focus"]))

    st.table(
        {
            "Company": [row[0] for row in score_table],
            "Score": [row[1] for row in score_table],
            "Verdict": [row[2] for row in score_table],
            "Focus Area": [row[3] for row in score_table],
        }
    )
