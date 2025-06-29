import os
import subprocess
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
from pathlib import Path
import re

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
            "You are an expert educator and Manim animator using Python. "
            "Given a student's text prompt, return three things:\n"
            "1. A valid Manim Python scene as raw code ONLY. "
            "Use only Manim Community v0.19-compatible features. "
            "Use Tex or MathTex for any LaTeX text. Escape all special characters properly. "
            "For line breaks, use double backslashes (\\\\) instead of \\n. "
            "NEVER use raw \\n in any Tex/MathTex string. Wrap all long text appropriately. "
            "❗ IMPORTANT: Do NOT use ImageMobject or any external image files.\n"
            "Only use built-in shapes (e.g., Square, Circle), Text, Tex, MathTex, etc.\n\n"
            "2. A short natural-sounding narration (1–2 sentences).\n"
            "3. A plain chatbot-style explanation suitable for a student.\n\n"
            "Format your output as follows (NO MARKDOWN, NO EXTRA TEXT):\n"
            "[BEGIN CODE]\n<code>\n[END CODE]\n"
            "[BEGIN NARRATION]\n<text>\n[END NARRATION]\n"
            "[BEGIN EXPLANATION]\n<text>\n[END EXPLANATION]"
        )


        full_prompt = f"{system_instruction}\n\nUser prompt: {prompt}"
        response = model.generate_content(full_prompt)
        content = response.text

        # Extract code, narration, explanation
        code = narration = explanation = None

        if "[BEGIN CODE]" in content and "[END CODE]" in content:
            raw_code = content.split("[BEGIN CODE]")[1].split("[END CODE]")[0].strip()
            code = raw_code.replace("```python", "").replace("```", "").strip()

        if "[BEGIN NARRATION]" in content and "[END NARRATION]" in content:
            narration = content.split("[BEGIN NARRATION]")[1].split("[END NARRATION]")[0].strip()

        if "[BEGIN EXPLANATION]" in content and "[END EXPLANATION]" in content:
            explanation = content.split("[BEGIN EXPLANATION]")[1].split("[END EXPLANATION]")[0].strip()

        if not code:
            return jsonify({
                "error": "Could not extract valid code from the model response."
            }), 500

        # Save Manim code to temp_scene.py
        backend_dir = Path(__file__).parent
        temp_scene_path = backend_dir / "temp_scene.py"
        temp_scene_path.write_text(code)

        # Extract Scene class name
        match = re.search(r"class\s+(\w+)\s*\(Scene\):", code)
        if not match:
            return jsonify({"error": "No valid Scene class found in generated code."}), 500
        scene_class_name = match.group(1)

        # Output folder for video
        output_dir = backend_dir / "static" / "videos"
        output_dir.mkdir(parents=True, exist_ok=True)
        video_filename = "output_video.mp4"
        video_path = output_dir / video_filename

        try:
            subprocess.run([
                "manim", str(temp_scene_path), scene_class_name,
                "--format", "mp4",
                "--fps", "30",
                "--output_file", str(video_path)
            ], check=True)


            video_url = f"http://localhost:5000/static/videos/{video_filename}"

        except subprocess.CalledProcessError as e:
            return jsonify({
                "error": "Manim render failed. Check your LaTeX syntax or Tex() usage.",
                "details": str(e),
                "code": code,
                "narration": narration,
                "explanation": explanation,
                "video_url": None
            }), 500
        
        print("=== Sending JSON to frontend ===")
        print({
            "code": code,
            "narration": narration,
            "explanation": explanation,
            "video_url": video_url
        })

        return jsonify({
            "code": code,
            "narration": narration,
            "explanation": explanation,
            "video_url": video_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/static/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory('static/videos', filename)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)