from flask import Flask, request, jsonify, send_file, redirect
from flask_cors import CORS
from app.pdf_generator import generate_pdf
import os
import traceback
import threading
from werkzeug.serving import make_server

# Flask uygulamasını doğrudan tanımlayın
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


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
    return jsonify({"message": "API is running on HTTPS!"}), 200

@app.before_request
def redirect_to_https():
    # HTTP'den HTTPS'e otomatik yönlendirme
    if request.url.startswith('http://'):
        return redirect(request.url.replace('http://', 'https://'), code=301)


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
        pdf_url = f"https://apideneme.viselab.net/download-pdf/{os.path.basename(pdf_path)}"

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
        # PDF dosya adının sonuna .pdf ekle
        if not filename.endswith('.pdf'):
            filename += '.pdf'

        # Dosya yolunu oluştur
        file_path = os.path.join(os.getcwd(), 'static/generated_offers', filename)
        print(f"[DEBUG] PDF dosya yolu: {file_path}")

        # Eğer dosya yoksa hata döndür
        if not os.path.exists(file_path):
            print(f"[ERROR] Dosya bulunamadı: {file_path}")
            return jsonify({"error": "File not found"}), 404

        # Dosyayı indirilebilir olarak gönder
        print(f"[DEBUG] Dosya indiriliyor: {file_path}")
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )
    except Exception as e:
        print(f"[ERROR] PDF indirme sırasında hata: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# HTTP Yönlendirme için ayrı bir sunucu başlat
class RedirectHTTPToHTTPS(threading.Thread):
    def run(self):
        http_app = Flask(__name__)

        @http_app.route('/', defaults={'path': ''})
        @http_app.route('/<path:path>')
        def redirect_to_https(path):
            # HTTP isteklerini HTTPS'e yönlendir
            return redirect(f"https://{request.host}/{path}", code=301)

        # HTTP sunucusunu başlat (Port 80)
        make_server('0.0.0.0', 80, http_app).serve_forever()

# HTTP yönlendirme başlat
RedirectHTTPToHTTPS().start()


if __name__ == '__main__':
    RedirectHTTPToHTTPS().start()  # HTTP'den HTTPS'e yönlendirme yapar

    # Flask uygulamasını HTTPS olmadan çalıştır (Nginx yönetecek)
    port = 8443  # Nginx, talepleri bu porta yönlendirecek
    app.run(debug=True, host='0.0.0.0', port=port)
