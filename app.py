from flask import Flask, request, jsonify
from google import genai
import os

# Initialize Flask
app = Flask(__name__)

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# Prompt template
EVAL_PROMPT = """Evaluate the quality of the Russian translation.
Source (English): "{prompt}"
Translation (Russian): "{response}"

Give a quality score from 0.0 (unacceptable) to 2.0 (perfect).
Only return the numeric score, no explanation."""


def eval_translation(source: str, translation: str) -> float:
    """Evaluate translation quality using Gemini API."""
    chat = client.chats.create(model="gemini-2.0-flash")
    response = chat.send_message(
        message=EVAL_PROMPT.format(prompt=source, response=translation)
    )
    return float(response.text.strip())


@app.route("/evaluate", methods=["POST"])
def evaluate():
    """
    POST endpoint: expects JSON with 'source' and 'translation'.
    Example:
    {
      "source": "Hello world",
      "translation": "Привет мир"
    }
    """
    data = request.get_json()
    source = data.get("source")
    translation = data.get("translation")

    if not source or not translation:
        return jsonify({"error": "Both 'source' and 'translation' are required"}), 400

    score = eval_translation(source, translation)
    return jsonify({"score": score})


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        source = request.form.get("source")
        translation = request.form.get("translation")

        if not source or not translation:
            return "Both fields are required", 400

        score = eval_translation(source, translation)
        return f"<h3>Score: {score}</h3><a href='/'>Go back</a>"

    return """
    <h2>LLM Translation Quality Evaluator</h2>
    <form method="post">
      <label>Source (English):</label><br>
      <input type="text" name="source" style="width:300px"><br><br>
      <label>Translation (Russian):</label><br>
      <input type="text" name="translation" style="width:300px"><br><br>
      <input type="submit" value="Evaluate">
    </form>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
