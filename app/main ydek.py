from flask import Flask, request, jsonify
from flask_cors import CORS
from app.pdf_generator import generate_pdf
import os

def create_app():
    """
    Flask uygulamasını oluşturur ve yapılandırır.
    """
    app = Flask(__name__)
    CORS(app)  # CORS'u etkinleştir

    @app.route('/generate-pdf', methods=['POST'])
    def generate_pdf_route():
        try:
            data = request.get_json()

            # Eksik veri kontrolü
            if not data or not data.get("items", []):
                return jsonify({"error": "Invalid data provided"}), 400

            # PDF oluştur
            pdf_path = generate_pdf(data)  # Dosya yolu: "static/generated_offers/file.pdf"
            #pdf_path = "static/generated_offers/test.pdf"

            # WebGL için tam URL oluştur
            #pdf_url = f"http://127.0.0.1:5000/{pdf_path.replace('static/', '')}"

            if pdf_path.startswith("http"):
                pdf_url = pdf_path  # Eğer pdf_path tam URL içeriyorsa direkt kullan
            else:
                pdf_url = f"http://127.0.0.1:5000/{pdf_path.lstrip('/')}"  # Baştaki "/"'yi kaldır

            return jsonify({
                "pdf_generated": True,
                "message": "PDF başarıyla oluşturuldu.",
                "pdf_path": pdf_url  # WebGL için tam erişim URL'si
            }), 200

        except Exception as e:
            # Hata durumunda loglama ve hata mesajı
            return jsonify({"error": f"Hata oluştu: {str(e)}"}), 500


    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=5000)
