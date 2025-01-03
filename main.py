from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from app.pdf_generator import generate_pdf
import os
import traceback
import jwt
import datetime

SECRET_KEY = "MATAPI290523"


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

download_tokens = {}

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf_route():
    try:
        # Gelen veriyi kontrol edin
        data = request.get_json()
        if not data or not data.get("items", []):
            return jsonify({"error": "Invalid data provided"}), 400

        # PDF dosyasının yolunu oluştur
        pdf_path = os.path.join(os.getcwd(), 'static/generated_offers/example.pdf')
        if not os.path.exists(pdf_path):
            with open(pdf_path, 'w') as f:
                f.write("Dummy PDF content for testing purposes.")

        # JWT Token oluştur (5 dakika geçerli olacak)
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        token = jwt.encode({"file_path": pdf_path, "exp": expiration_time}, SECRET_KEY, algorithm="HS256")

        # Secure-download endpoint URL'si
        secure_url = f"https://apideneme.viselab.net/secure-download?token={token}"

        return jsonify({
            "pdf_generated": True,
            "message": "PDF başarıyla oluşturuldu.",
            "pdf_path": secure_url
        }), 200

    except Exception as e:
        return jsonify({"error": f"Hata oluştu: {str(e)}"}), 500

@app.route('/secure-download', methods=['GET'])
def secure_download():
    try:
        token = request.args.get("token")

        # Token doğrulama
        if not token:
            return jsonify({"error": "Missing token"}), 403

        try:
            # Token çözümleme
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            file_path = decoded_token["file_path"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 403

        # Dosya kontrolü
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        filename = os.path.basename(file_path)
        download_link = f"https://apideneme.viselab.net/download-pdf/{filename}"

        # HTML ile indirme bağlantısı döndür
        return f"""
        <html>
            <head>
                <title>Downloading...</title>
                <script>
                    setTimeout(function() {{
                        window.location.href = "{download_link}";
                    }}, 1000);
                </script>
            </head>
            <body>
                <h2>Your file is being downloaded...</h2>
                <p>If the download doesn't start automatically, <a href="{download_link}">click here</a>.</p>
            </body>
        </html>
        """
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/download-pdf/<filename>', methods=['GET'])
def download_pdf(filename):
    try:
        file_path = os.path.join(os.getcwd(), 'static/generated_offers', filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"An error occurred in download-pdf: {str(e)}"}), 500


if __name__ == '__main__':
    # Flask uygulamasını HTTPS olmadan çalıştır (Nginx yönetecek)
    port = 8443  # Nginx talepleri bu porta yönlendirecek
    app.run(debug=True, host='0.0.0.0', port=port)
