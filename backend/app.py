import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        system_instruction = (
            "You are an expert educator and Manim animator. "
            "Given a student's text prompt, return three things:\n"
            "1. A valid Manim Python scene as raw code (no markdown, no explanation).\n"
            "2. A short natural-sounding narration to describe the animation.\n"
            "3. A plain language explanation suitable for chatbot conversation.\n\n"
            "Format:\n"
            "[BEGIN CODE]\n<code>\n[END CODE]\n"
            "[BEGIN NARRATION]\n<text>\n[END NARRATION]\n"
            "[BEGIN EXPLANATION]\n<text>\n[END EXPLANATION]"
        )

        full_prompt = f"{system_instruction}\n\nUser prompt: {prompt}"
        response = model.generate_content(full_prompt)
        content = response.text

        # Extract code, narration, and explanation
        code = narration = explanation = None

        if "[BEGIN CODE]" in content and "[END CODE]" in content:
            code = content.split("[BEGIN CODE]")[1].split("[END CODE]")[0].strip()

        if "[BEGIN NARRATION]" in content and "[END NARRATION]" in content:
            narration = content.split("[BEGIN NARRATION]")[1].split("[END NARRATION]")[0].strip()

        if "[BEGIN EXPLANATION]" in content and "[END EXPLANATION]" in content:
            explanation = content.split("[BEGIN EXPLANATION]")[1].split("[END EXPLANATION]")[0].strip()

        return jsonify({
            "code": code,
            "narration": narration,
            "explanation": explanation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
