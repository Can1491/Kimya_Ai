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

def get_working_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print(f"Sistemde bulunan aktif modeller: {models}")
        
        for target in ['models/gemini-1.5-flash', 'models/gemini-pro', 'models/gemini-1.0-pro']:
            if target in models:
                print(f"Seçilen Model: {target}")
                return genai.GenerativeModel(target)
                
        return genai.GenerativeModel(models[0])
    except Exception as e:
        print(f"Model listeleme hatası: {e}")
        
        return genai.GenerativeModel('gemini-pro')

model = get_working_model()

@app.route("/")
def home():
    return "<h1>Kimya Sunucusu Aktif!</h1>"

@app.route("/solve", methods=["POST"])
def solve():
    try:
        data = request.get_json()
        reaction = data.get("reaction", "")
        print(f"Gelen İstek: {reaction}")

        prompt = f"Kimya uzmanı ol. '{reaction}' reaksiyonunu analiz et. Sadece şu JSON formatında cevap ver: {{\"products\": \"...\", \"balanced\": \"...\"}}"
        
        response = model.generate_content(prompt)
        
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return jsonify(json.loads(match.group(0)))
        return jsonify({"products": "Hata", "balanced": "JSON formatı bulunamadı"}), 500

    except Exception as e:
        print(f"KRİTİK HATA: {str(e)}")
        return jsonify({"products": "Sunucu Hatası", "balanced": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
