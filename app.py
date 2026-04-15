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
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print(f"Sistemde bulunan aktif modeller: {available_models}")
        
        priority_list = [
            'models/gemini-2.5-flash', 
            'models/gemini-1.5-flash', 
            'models/gemini-2.0-flash',
            'models/gemini-1.5-pro'
        ]
        
        for target in priority_list:
            if target in available_models:
                print(f"Seçilen Model: {target}")
                return genai.GenerativeModel(target)
        if available_models:
            print(f"Varsayılan model seçildi: {available_models[0]}")
            return genai.GenerativeModel(available_models[0])
            
    except Exception as e:
        print(f"Model listeleme hatası: {e}")
    
    return genai.GenerativeModel('gemini-1.5-flash')
model = get_working_model()

@app.route("/")
def home():
    return "<h1>Kimya Sunucusu Aktif!</h1>"

@app.route("/solve", methods=["POST"])
def solve():
    try:
        data = request.get_json()
        if not data or "reaction" not in data:
            return jsonify({"products": "Hata", "balanced": "İstek boş olamaz"}), 400
            
        reaction = data.get("reaction", "")
        print(f"Gelen İstek: {reaction}")

        prompt = (
            f"Sen bir kimya uzmanısın. '{reaction}' reaksiyonunun ürünlerini bul ve denklemi denkleştir. "
            f"Yanıtı sadece ve sadece geçerli bir JSON formatında ver. "
            f"Format şu şekilde olmalı: {{\"products\": \"...\", \"balanced\": \"...\"}}"
        )    
        response = model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return jsonify(json.loads(json_str))
        return jsonify({"products": "Hata", "balanced": "AI geçerli bir JSON yanıtı oluşturamadı"}), 500

    except Exception as e:
        error_str = str(e)
        print(f"KRİTİK HATA: {error_str}")
        
        if "429" in error_str or "quota" in error_str.lower():
            return jsonify({"products": "Kota Doldu", "balanced": "Günlük limitinize ulaştınız."}), 429
            
        return jsonify({"products": "Sunucu Hatası", "balanced": error_str}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
