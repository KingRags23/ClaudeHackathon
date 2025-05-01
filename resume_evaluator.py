import dash
from dash import html, dcc, Input, Output, State, ctx
import base64
import fitz  # PyMuPDF
import anthropic
import tempfile
import os

# Secure Claude setup using env var
client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

FAANG_COMPANIES = {
    "Meta": "System design, large-scale systems, modern frontend/backend stacks (React, GraphQL), measurable user impact, and team leadership",
    "Amazon": "Leadership principles (ownership, customer obsession), AWS ecosystem, quantifiable outcomes, performance and cost improvements",
    "Apple": "Swift/Objective-C, UX focus, hardware/software integration, CI/CD, reusable components, and performance optimization",
    "Netflix": "Cloud infrastructure (AWS), scalable systems, personalization, A/B testing, microservices, and fast-paced innovation",
    "Google": "Algorithms, distributed systems, ML (TensorFlow), innovation, research collaboration, and cross-functional teamwork"
}

# Claude prompt for strict ATS evaluation
def get_claude_score_feedback(company, focus, resume_text):
    prompt = f"""
You are an expert ATS evaluator for {company}. Their hiring bar is very high and strict.

Evaluate the resume below based on how well it matches {company}'s hiring criteria:
{focus}

Be very critical. Only give a score above 70 if it is truly exceptional. Be specific in your feedback.

Resume:
\"\"\"
{resume_text}
\"\"\"

Return the result in this format exactly:

Score: <score>/100
Feedback:
- <bullet point>
- <bullet point>
- <bullet point>
"""

    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

# Claude prompt for tailored cover letter generation
def generate_cover_letter(company, resume_text):
    prompt = f"""
You are a career assistant for a student applying to a software engineering internship at {company}.

Based on the resume below, write a personalized, 100–150 word cover letter that highlights their technical strengths, passion, and why they're a good fit for {company}'s culture and values.

Be specific to {company}'s domain.

Resume:
\"\"\"
{resume_text}
\"\"\"
"""
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

# PDF resume reader
def extract_text_from_pdf(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(decoded)
        tmp_path = tmp.name
    doc = fitz.open(tmp_path)
    text = "\n".join([page.get_text() for page in doc])
    os.remove(tmp_path)
    return text

# App layout
app = dash.Dash(__name__)
app.title = "FAANG ATS Evaluator"

app.layout = html.Div(style={"padding": "2rem", "fontFamily": "Arial"}, children=[
    html.H1("FAANG Resume Evaluator (Claude-Powered)", style={"textAlign": "center"}),
    dcc.Upload(
        id='upload-resume',
        children=html.Div(['📎 Drag and Drop or ', html.A('Upload a PDF Resume')]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '10px',
            'textAlign': 'center', 'marginBottom': '20px'
        },
        multiple=False
    ),
    html.Div(id='report-section'),
    html.Div(id='cover-letter-output', style={"marginTop": "2rem"})
])

# State to hold resume text
resume_store = {"text": ""}

@app.callback(
    Output('report-section', 'children'),
    Input('upload-resume', 'contents'),
    State('upload-resume', 'filename')
)
def handle_resume_upload(contents, filename):
    if contents is None:
        return None

    resume_text = extract_text_from_pdf(contents)
    resume_store["text"] = resume_text

    reports = []

    for company, focus in FAANG_COMPANIES.items():
        result = get_claude_score_feedback(company, focus, resume_text)
        score_line = next((line for line in result.splitlines() if "Score" in line), "Score: N/A")
        feedback_lines = [line for line in result.splitlines() if line.startswith("-")]

        reports.append(html.Div(style={"border": "1px solid #ddd", "borderRadius": "10px", "padding": "1rem", "marginBottom": "1.5rem"}, children=[
            html.H2(f"{company}"),
            html.P(f"🎯 Focus: {focus}", style={"fontStyle": "italic"}),
            html.H4(score_line),
            html.Ul([html.Li(line[2:]) for line in feedback_lines]),
            html.Button(f"Generate Cover Letter for {company}", id=f"btn-{company}", n_clicks=0)
        ]))

    return reports

# Dynamically handle any cover letter generation
@app.callback(
    Output("cover-letter-output", "children"),
    [Input(f"btn-{company}", "n_clicks") for company in FAANG_COMPANIES.keys()]
)
def generate_letter_for_all(*clicks):
    triggered = ctx.triggered_id
    if triggered is None or resume_store["text"] == "":
        return None

    company = triggered.replace("btn-", "")
    with_cover = generate_cover_letter(company, resume_store["text"])

    return html.Div(style={"border": "2px solid #aaa", "padding": "1rem", "borderRadius": "10px"}, children=[
        html.H3(f"Cover Letter for {company}"),
        html.Pre(with_cover, style={"whiteSpace": "pre-wrap", "fontFamily": "Courier New"})
    ])

if __name__ == '__main__':
    app.run(debug=True)
