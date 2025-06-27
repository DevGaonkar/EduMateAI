import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv()

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        # Use latest SDK format
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": (
                    "You are an expert educator and Manim animator. "
                    "Given a teaching prompt, return two things:\n"
                    "1. A valid Python Manim scene as plain code (no markdown).\n"
                    "2. A short narration script that matches the animation.\n\n"
                    "Format:\n"
                    "[BEGIN CODE]\n<code>\n[END CODE]\n"
                    "[BEGIN NARRATION]\n<text>\n[END NARRATION]"
                )},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        # Extract text
        full_reply = response.choices[0].message.content

        # Parse code and narration
        code = narration = None
        if "[BEGIN CODE]" in full_reply and "[END CODE]" in full_reply:
            code = full_reply.split("[BEGIN CODE]")[1].split("[END CODE]")[0].strip()

        if "[BEGIN NARRATION]" in full_reply and "[END NARRATION]" in full_reply:
            narration = full_reply.split("[BEGIN NARRATION]")[1].split("[END NARRATION]")[0].strip()

        return jsonify({
            "code": code,
            "narration": narration
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
