from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from app.pdf_generator import generate_pdf
import os
import traceback

# Flask uygulamasını doğrudan tanımlayın
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# CORS başlıklarını tüm yanıtlara ekleyen fonksiyon
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API is running on HTTPS!"}), 200

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"[ERROR] Uygulama hatası: {e}")
    print("[TRACEBACK]")
    traceback.print_exc()  # Detaylı traceback loglama
    return jsonify({"error": str(e)}), 500

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf_route():
    try:
        data = request.get_json()

        if not data or not data.get("items", []):
            return jsonify({"error": "Invalid data provided"}), 400

        # PDF oluştur
        pdf_path = generate_pdf(data)

        if not os.path.exists(pdf_path):
            print(f"[ERROR] PDF oluşturulamadı: {pdf_path}")
            return jsonify({"error": "PDF oluşturulamadı"}), 500

        # PDF URL oluştur
        pdf_url = f"https://apideneme.viselab.net/download-pdf/{os.path.basename(pdf_path)}"
        print(f"[DEBUG] Oluşturulan PDF URL: {pdf_url}")

        return jsonify({
            "pdf_generated": True,
            "message": "PDF başarıyla oluşturuldu.",
            "pdf_path": pdf_url
        }), 200

    except Exception as e:
        print(f"[ERROR] generate_pdf hatası: {e}")
        return jsonify({"error": f"Hata oluştu: {str(e)}"}), 500


@app.route('/download-pdf/<filename>', methods=['GET'])
def download_pdf(filename):
    try:
        if not filename.endswith('.pdf'):
            filename += '.pdf'

        file_path = os.path.join(os.getcwd(), 'static/generated_offers', filename)
        if not os.path.exists(file_path):
            print(f"[ERROR] Dosya bulunamadı: {file_path}")
            return jsonify({"error": "File not found"}), 404

        print(f"[DEBUG] Dosya indiriliyor: {file_path}")
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    except Exception as e:
        print(f"[ERROR] PDF indirme sırasında hata: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    # Flask uygulamasını HTTPS olmadan çalıştır (Nginx yönetecek)
    port = 8443  # Nginx talepleri bu porta yönlendirecek
    app.run(debug=True, host='0.0.0.0', port=port)
