from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from app.pdf_generator import generate_pdf
import os
import traceback

# Flask uygulamasını doğrudan tanımlayın
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://candid-longma-2cc50d.netlify.app"}})


# CORS başlıklarını tüm yanıtlara ekleyen fonksiyon
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'  # Herkese izin ver
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API is running!"}), 200

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"[ERROR] Uygulama hatası: {e}")
    print("[TRACEBACK]")
    traceback.print_exc()  # Detaylı traceback loglama
    return jsonify({"error": str(e)}), 500

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf_route():
    """if request.method == 'OPTIONS':
        # CORS preflight response
        return jsonify({'message': 'CORS preflight check passed'}), 200"""
    try:
        data = request.get_json()

        # Eksik veri kontrolü
        if not data or not data.get("items", []):
            return jsonify({"error": "Invalid data provided"}), 400

        # PDF oluştur
        pdf_path = generate_pdf(data)  # PDF dosya yolu

        # Eğer dosya başarıyla oluşturulduysa URL oluştur
        #pdf_url = f"{request.host_url}download-pdf/{os.path.basename(pdf_path)}"
        pdf_url = f"http://3.89.98.40/download-pdf/{os.path.basename(pdf_path)}"

        return jsonify({
            "pdf_generated": True,
            "message": "PDF başarıyla oluşturuldu.",
            "pdf_url": pdf_url  # Kullanıcı için indirme bağlantısı
        }), 200

    except Exception as e:
        return jsonify({"error": f"Hata oluştu: {str(e)}"}), 500

@app.route('/download-pdf/<filename>', methods=['GET'])
def download_pdf(filename):
    try:
        # Tam dosya yolu
        file_path = os.path.join(os.getcwd(), 'static/generated_offers', filename)
        print(f"[DEBUG] PDF dosya yolu: {file_path}")

        # Eğer dosya yoksa hata döndür
        if not os.path.exists(file_path):
            print(f"[ERROR] Dosya bulunamadı: {file_path}")
            return jsonify({"error": "File not found"}), 404

        # Dosyayı indirilebilir olarak gönder
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )
    except Exception as e:
        print(f"[ERROR] PDF indirme sırasında hata: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))  # AWS'de Port 80 kullan
    app.run(debug=True, host='0.0.0.0', port=port)
