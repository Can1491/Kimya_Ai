import os
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)

CORS(app)

api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-pro')
else:
    print("HATA: GEMINI_API_KEY bulunamadı! Render panelini kontrol et.")

@app.route("/")
def home():
    return "<h1>Kimya AI Sunucusu Aktif!</h1><p>API Anahtarı Durumu: {}</p>".format("Yüklendi" if api_key else "Eksik!")

@app.route("/solve", methods=["POST"])
def solve():
    try:

        data = request.get_json()
        if not data or "reaction" not in data:
            return jsonify({"products": "Hata", "balanced": "Veri gönderilmedi"}), 400
        
        reaction = data.get("reaction", "")
        print(f"Gelen İstek: {reaction}") 

        if not api_key:
            return jsonify({"products": "Hata", "balanced": "Sunucuda API anahtarı ayarlanmamış!"}), 500

        prompt = (
            f"Sen bir kimya uzmanısın. Şu reaksiyonu analiz et: '{reaction}'. "
            f"Cevabı SADECE şu JSON formatında ver, başka açıklama yapma: "
            f"{{\"products\": \"oluşan ürünler\", \"balanced\": \"denkleşmiş tam denklem\"}}"
        )

        response = model.generate_content(prompt)

        text_response = response.text
        print(f"AI Yanıtı: {text_response}")

        match = re.search(r'\{.*\}', text_response, re.DOTALL)
        
        if match:
            json_data = json.loads(match.group(0))
            return jsonify(json_data)
        else:
            return jsonify({"products": "Hata", "balanced": "AI geçerli bir yanıt oluşturamadı"}), 500

    except Exception as e:

        print(f"--- KRİTİK HATA BAŞLANGICI ---")
        print(f"Hata Mesajı: {str(e)}")
        print(f"--- KRİTİK HATA BITIŞI ---")
        return jsonify({
            "products": "Sunucu hatası oluştu",
            "balanced": f"Detay: {str(e)}"
        }), 500

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
