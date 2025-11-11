from flask import Flask, jsonify, request, render_template_string
from markupsafe import Markup, escape
import json
import random

app = Flask(__name__)

# Load questions from JSON file
import os

questions_path = os.path.join(os.path.dirname(__file__), "questions.json")
if os.path.exists(questions_path):
    with open(questions_path) as f:
        QUESTIONS = json.load(f)
    print(f"✅ Loaded {len(QUESTIONS)} questions from {questions_path}")
else:
    print(f"⚠️ questions.json not found at {questions_path}")
    QUESTIONS = []

def render_text_safe(text):
    """Convert Markdown-style backticks to HTML <code> tags and escape everything else safely."""
    # Escape HTML-sensitive chars first
    escaped = escape(text)
    # Replace `inline code` with <code> tags
    return Markup(escaped.replace("`", "<code>").replace("</code><code>", "`"))  # fix double replacements

@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>DevOps Mock Assessment</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f8f9fa; }
            h1 { color: #1a1a1a; }
            .question { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; box-shadow: 0 0 5px rgba(0,0,0,0.1); }
            code { background: #eee; padding: 2px 5px; border-radius: 4px; font-family: monospace; color: #d63384; }
            button { padding: 10px 15px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h1>DevOps Mock Assessment</h1>
        <p>Click the button below to load your 25-question practice test.</p>
        <button onclick="loadTest()">Load Questions</button>
        <div id="content"></div>

        <script>
            async function loadTest() {
                const res = await fetch('/questions');
                const data = await res.json();
                const container = document.getElementById('content');
                container.innerHTML = '';
                data.forEach((q, i) => {
                    const div = document.createElement('div');
                    div.className = 'question';
                    div.innerHTML =
                        '<b>Q' + (i + 1) + ':</b> ' + q.question_html +
                        '<ul>' + q.options.map(o => '<li>' + o + '</li>').join('') + '</ul>';
                    container.appendChild(div);
                });
            }
        </script>
    </body>
    </html>
    """)

@app.route("/questions")
def get_all_questions():
    # 🟢 Pre-render question & options safely for HTML
    rendered = []
    for q in QUESTIONS:
        q_copy = q.copy()
        q_copy["question_html"] = str(render_text_safe(q["question"]))
        q_copy["options"] = [str(render_text_safe(o)) for o in q["options"]]
        rendered.append(q_copy)
    return jsonify(rendered)

@app.route("/health")
def health():
    return jsonify(status="healthy")

@app.route("/random")
def get_random_questions():
    count = int(request.args.get("count", 10))
    sample = random.sample(QUESTIONS, min(count, len(QUESTIONS)))
    return jsonify(sample)

@app.route("/submit", methods=["POST"])
def submit_answers():
    data = request.json.get("answers", {})
    score = 0
    results = []

    for q in QUESTIONS:
        qid = str(q["id"])
        correct = q["answer"]
        user_answer = data.get(qid)
        is_correct = user_answer == correct
        if is_correct:
            score += 1
        results.append({
            "id": qid,
            "question": q["question"],
            "your_answer": user_answer,
            "correct_answer": correct,
            "result": "✅" if is_correct else "❌"
        })

    return jsonify({
        "score": f"{score}/{len(QUESTIONS)}",
        "details": results
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
