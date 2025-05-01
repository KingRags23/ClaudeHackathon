# ClaudeHackathon
# 🧠 easyATS — FAANG Resume Evaluator (ClaudeHackathon)

Ever wonder why your resume keeps getting ghosted? It’s probably in an ATS dumpster.  
**easyATS** simulates a FAANG-style Applicant Tracking System using Anthropic’s Claude to scan, roast, and revive resumes before recruiters click "nope."

## 🚀 Features

- ✅ Upload a PDF resume
- 🤖 Score your resume against Meta, Amazon, Apple, Netflix, and Google criteria
- 🧠 Claude-generated feedback tailored to each company
- 📝 Optional cover letter generation
- 📊 Real-time Streamlit UI

## 🛠 Built With

- Python
- Streamlit
- PyMuPDF (`fitz`) for PDF parsing
- Anthropic Claude API (model: `claude-3-opus-20240229`)
- Regex & custom scoring logic

## 💻 Run Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/easyATS.git
   cd easyATS
