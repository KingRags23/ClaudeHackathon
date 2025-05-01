
import streamlit as st
import fitz  # PyMuPDF
import re
import tempfile
import os
import anthropic

# Initialize Claude
client = anthropic.Anthropic(api_key="CLAUDE_API_KEY")

st.set_page_config(page_title="FAANG Resume ATS Evaluator", layout="wide")

FAANG_CRITERIA = {
    "Meta": {
        "keywords": ["React.js", "GraphQL", "JavaScript", "Python", "PHP", "Hack", "microservices", "scalable systems",
                     "engagement", "feed ranking", "load balancing", "developer tooling", "mentored", "collaborated",
                     "production issues"],
        "focus": "System design, impact metrics, scalable systems, team leadership"
    },
    "Amazon": {
        "keywords": ["AWS", "DynamoDB", "Lambda", "S3", "EC2", "serverless", "Agile", "ownership", "customer obsession",
                     "automated", "latency", "deployment", "high-traffic"],
        "focus": "Leadership principles, AWS stack, measurable results, scalability"
    },
    "Apple": {
        "keywords": ["Swift", "Objective-C", "Xcode", "iOS", "macOS", "Unix", "CI/CD", "debugged", "hybrid apps",
                     "reusable components", "design verification", "load balancing", "communication"],
        "focus": "UX, Apple ecosystem, hardware/software integration, reusable code"
    },
    "Netflix": {
        "keywords": ["AWS", "Kubernetes", "microservices", "streaming", "buffering", "personalization", "A/B testing",
                     "automation", "monitoring", "alerting", "fast-paced", "data-driven"],
        "focus": "Scalable backend, streaming optimization, rapid deployment, data-first thinking"
    },
    "Google": {
        "keywords": ["Python", "C++", "Java", "Go", "MapReduce", "distributed systems", "search accuracy",
                     "TensorFlow", "BigQuery", "mentored", "CI/CD", "RESTful APIs", "privacy"],
        "focus": "Algorithms, distributed systems, ML, research collaboration"
    }
}

def score_resume(text, keywords):
    score = 0
    for word in keywords:
        if word.lower() in text.lower():
            score += 5
    quantified = re.findall(r'\d+%|\$\d+|[0-9]+ users?', text)
    score += len(quantified) * 3
    verbs = ["implemented", "designed", "optimized", "deployed", "collaborated", "led", "automated"]
    score += sum(text.lower().count(v) for v in verbs)
    return min(score, 100)

def get_claude_feedback(company, resume_text, score, focus):
    prompt = (
        f"You are an ATS resume reviewer for {company}. "
        f"The resume scored {score}/100. The company's ATS prioritizes: {focus}. "
        f"Provide 2-3 concise, specific suggestions to improve the resume. "
        f"Resume text:\n\n---\n{resume_text}\n---"
    )
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

def generate_cover_letter(company, resume_text):
    prompt = (
        f"Based on this resume, write a short cover letter (300 - 400 words) applying for a software engineering internship at {company}. "
        f"Make it tailored, technically credible, and enthusiastic.\n\nResume:\n{resume_text}"
    )
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

# Streamlit UI
st.title("🎯 FAANG Resume ATS Evaluator with Claude")
uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
enable_cover_letter = st.checkbox("Generate cover letter (optional)")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    doc = fitz.open(tmp_path)
    resume_text = "\n".join([page.get_text() for page in doc])
    os.remove(tmp_path)

    st.subheader("📄 Resume Preview")
    st.text_area("Extracted Resume Text", resume_text, height=300)

    st.subheader("📊 FAANG ATS Results")
    for company, data in FAANG_CRITERIA.items():
        score = score_resume(resume_text, data["keywords"])
        verdict = "✅ Likely" if score >= 70 else "⚠️ Borderline" if score >= 50 else "❌ Unlikely"

        with st.expander(f"{company} — Score: {score}/100 — {verdict}"):
            st.write(f"**Focus:** {data['focus']}")
            with st.spinner("🔍 Claude is analyzing..."):
                feedback = get_claude_feedback(company, resume_text, score, data["focus"])
            st.write("**📌 Suggestions from Claude:**")
            st.write(feedback)

            if enable_cover_letter:
                with st.spinner("✍️ Claude is generating a cover letter..."):
                    letter = generate_cover_letter(company, resume_text)
                st.write("**📄 Cover Letter:**")
                st.code(letter)
