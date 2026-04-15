import os
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')


@app.route("/")
def home():
    return "Kimya AI Sunucusu Aktif!"


@app.route("/solve", methods=["POST"])
def solve():
    try:
        data = request.get_json()
        reaction = data.get("reaction", "")

        prompt = f"Kimya uzmanı olarak bu reaksiyonu çöz: '{reaction}'. Sadece şu JSON formatında cevap ver: {{\"products\": \"ürünler\", \"balanced\": \"denkleşmiş hali\"}}"

        response = model.generate_content(prompt)
        # Yanıtın içinden JSON'ı ayıkla
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return jsonify(json.loads(match.group(0)))
        return jsonify({"products": "Hata", "balanced": "JSON bulunamadı"}), 500
    except Exception as e:
        return jsonify({"products": "Hata", "balanced": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))