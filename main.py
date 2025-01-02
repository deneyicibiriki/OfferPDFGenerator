from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from app.pdf_generator import generate_pdf
import os
import traceback
import uuid
import time
import threading


# Flask uygulamasını doğrudan tanımlayın
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

download_tokens = {}

def generate_unique_token():
    while True:
        token = str(uuid.uuid4())
        if token not in download_tokens:
            return token

def clean_expired_tokens():
    while True:
        current_time = time.time()
        expired_tokens = [token for token, data in download_tokens.items() if current_time > data["expires_at"]]

        for token in expired_tokens:
            del download_tokens[token]

        print(f"[DEBUG] Expired tokens cleaned. Remaining tokens: {len(download_tokens)}")
        time.sleep(60)  # Her 60 saniyede bir kontrol eder

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
        print("[DEBUG] JSON Verisi Alındı:", data)
        pdf_path = generate_pdf(data)

        token = generate_unique_token()
        download_tokens[token] = {
            "file_path": pdf_path,
            "expires_at": time.time() + 60,  # 60 saniye geçerli
        }



        if not pdf_path:
            print("[ERROR] generate_pdf fonksiyonu boş değer döndürdü.")
            return jsonify({"error": "PDF oluşturulamadı"}), 500

            # Eğer dosya mevcut değilse hata ver
        if not os.path.exists(pdf_path):
            print(f"[ERROR] PDF oluşturulamadı: {pdf_path}")
            return jsonify({"error": "PDF oluşturulamadı"}), 500

        # PDF URL oluştur
        #pdf_url = f"https://apideneme.viselab.net/download-pdf/{os.path.basename(pdf_path)}"
        secure_url = f"https://apideneme.viselab.net/secure-download?token={token}"
        #print(f"[DEBUG] Oluşturulan PDF URL: {pdf_url}")
        print(f"[DEBUG] Oluşturulan PDF URL: {secure_url}")

        return jsonify({
            "pdf_generated": True,
            "message": "PDF başarıyla oluşturuldu.",
            #"pdf_path": pdf_url
            "pdf_path": secure_url  # Burada artık secure-download döneceğiz
        }), 200

    except Exception as e:

        print(f"[ERROR] generate_pdf hatası: {e}")
        return jsonify({"error": f"Hata oluştu: {str(e)}"}), 500

@app.route('/secure-download', methods=['GET'])
def secure_download():
    try:
        token = request.args.get("token")

        # Token kontrolü
        if not token or token not in download_tokens:
            return """
            <html>
                <body>
                    <h2>Invalid or expired token</h2>
                    <p>The requested link is no longer valid. Please generate a new PDF to download.</p>
                </body>
            </html>
            """, 403

        token_data = download_tokens[token]
        file_path = token_data["file_path"]

        # Token süresi dolmuş mu?
        if time.time() > token_data["expires_at"]:
            del download_tokens[token]
            return """
            <html>
                <body>
                    <h2>Token expired</h2>
                    <p>The requested link has expired. Please generate a new PDF to download.</p>
                </body>
            </html>
            """, 403

        # Dosya adı ve download linki
        filename = os.path.basename(file_path)
        download_link = f"https://apideneme.viselab.net/download-pdf/{filename}"

        # HTML mesajı döndür
        return f"""
        <html>
            <head>
                <title>Downloading...</title>
                <script>
                    // 1 saniye içinde indirmenin başlaması
                    setTimeout(function() {{
                        window.location.href = "{download_link}";
                    }}, 1000);
                </script>
            </head>
            <body>
                <h2>Your file is downloading...</h2>
                <p>If the download doesn't start automatically, <a href="{download_link}">click here</a>.</p>
            </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
            <body>
                <h2>An error occurred</h2>
                <p>{str(e)}</p>
            </body>
        </html>
        """, 500

@app.route('/download-pdf/<filename>', methods=['GET'])
def download_pdf(filename):
    try:
        if not filename.endswith('.pdf'):
            filename += '.pdf'

        file_path = os.path.join(os.getcwd(), 'static/generated_offers', filename)
        print(f"[DEBUG] -----Download pdf fonksiyonu: PDF dosya yolu: {file_path}")
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
        print(f"[DEBUG] File sent successfully: {file_path}")
        return response


    except Exception as e:
        print(f"[ERROR] PDF indirme sırasında hata: {e}")
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    threading.Thread(target=clean_expired_tokens, daemon=True).start()
    # Flask uygulamasını HTTPS olmadan çalıştır (Nginx yönetecek)
    port = 8443  # Nginx talepleri bu porta yönlendirecek
    app.run(debug=True, host='0.0.0.0', port=port)
