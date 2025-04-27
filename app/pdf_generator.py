from fpdf import FPDF
import os
import datetime
import re



def convert_to_float(value):
    try:
        # Eğer gelen veri virgüllü ise noktaya çevir
        if isinstance(value, str) and ',' in value:
            value = value.replace(',', '.')
        return float(value)
    except ValueError as e:
        print(f"[ERROR] Sayıyı float'a dönüştürürken hata oluştu: {e}")
        return None

def generate_pdf(data):
    print("[DEBUG] generate_pdf function called.")

    try:
        # Gelen veriyi kontrol et ve dönüştür
        for item in data.get("items", []):
            if "price" in item:  # "price" yerine kendi sayısal alanını yaz
                item["price"] = convert_to_float(item["price"])

        # Burada PDF oluşturma işlemlerini yap
        print("[DEBUG] Dönüştürülmüş veri:", data)

    except Exception as e:
        print(f"[ERROR] PDF oluşturulurken hata oluştu: {e}")

    try:
        # Date details
        creation_date = datetime.datetime.now().strftime("%d/%m/%Y")
        valid_until_date = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%d/%m/%Y")
        print(f"[DEBUG] Creation date: {creation_date}, Valid until: {valid_until_date}")

        # Generate reference number
        # Customer type için harita
        customer_type = data.get("CustomerType", "None").strip()

        # Eğer customer_type boşsa varsayılan "None" değerini kullan
        if not customer_type:
            customer_type = "None"

        customer_type_map = {
            "RegularRequester": "R",
            "ImportantRequester": "I",
            "Dealer": "D",
            "None": "N"  # Varsayılan değer
        }

        # Gelen customer_type'ı al


        # Haritadan uygun karakteri seç (default: 'N')
        customer_character = customer_type_map.get(customer_type, "N")

        # Klasörü oluştur
        output_folder = "static/generated_offers"
        os.makedirs(output_folder, exist_ok=True)

        # Var olan dosyaları taramak için regex
        pattern = re.compile(rf"PRE-{customer_character}-MK(\d+).pdf")

        # Mevcut en yüksek numarayı bul
        max_number = 0
        existing_files = os.listdir(output_folder)

        for file_name in existing_files:
            match = pattern.match(file_name)
            if match:
                max_number = max(max_number, int(match.group(1)))

        # Yeni referans numarası oluştur
        new_reference_no = f"{max_number + 1:04}"
        reference_number = f"PRE-{customer_character}-MK{new_reference_no}"
        output_path = f"/home/ec2-user/OfferPDFGenerator/static/generated_offers/{reference_number}.pdf"
        print(f"[DEBUG] PDF oluşturma başlıyor: {output_path}")
        print(f"[DEBUG] Generated reference number: {reference_number}")


        # Add extra details to data
        data["referenceNumber"] = reference_number
        data["creationDate"] = creation_date
        data["validUntilDate"] = valid_until_date

        # Create PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Add UTF-8 font support
        try:
            pdf.add_font("DejaVu", "", "static/fonts/DejaVuSans.ttf", uni=True)
            pdf.add_font("DejaVu", "I", "static/fonts/DejaVuSans-Oblique.ttf", uni=True)
            pdf.add_font("DejaVu", "B", "static/fonts/DejaVuSans-Bold.ttf", uni=True)
            print("[DEBUG] Fonts successfully added.")
        except Exception as e:
            print(f"[ERROR] Font addition error: {e}")
            raise


        # Add header
        # Logo and Company Details on the left

        try:
            # URL üzerinden logo ekleme
            logo_url = "https://apideneme.viselab.net/static/assets/logo.png"
            print(f"[DEBUG] Logo URL yükleniyor: {logo_url}")

            # URL üzerinden resmi eklemek için
            pdf.image(logo_url, x=10, y=8, w=50)  # Logo büyütüldü
            pdf.set_xy(10, 50)  # Position for text below the logo

            print("[DEBUG] Logo başarıyla eklendi.")
        except Exception as e:
            print(f"[ERROR] Logo eklenirken hata oluştu: {e}")
        """

        try:
            # Dosya sisteminden logo ekleme
            static_path = os.path.join(os.getcwd(), 'static/assets/logo.png')
            print(f"[DEBUG] Logo dosya yolu yükleniyor: {static_path}")

            if os.path.exists(static_path):
                pdf.image(static_path, x=10, y=8, w=50)  # Logo büyütüldü
                pdf.set_xy(10, 50)  # Position for text below the logo
                print("[DEBUG] Logo başarıyla eklendi.")
            else:
                print(f"[ERROR] Logo dosyası bulunamadı: {static_path}")
        except Exception as e:
                print(f"[ERROR] Logo eklenirken hata oluştu: {e}")
        """
        # F.Reg.
        pdf.set_font("DejaVu", "B", size=10)  # Bold font for label
        pdf.cell(20, 5, txt="F.Reg.:", align="L", border=0)  # Label
        pdf.set_font("DejaVu", size=10)  # Regular font for value
        pdf.cell(0, 5, txt="925 720 488 MVA", align="L", ln=True, border=0)  # Value

        # Email
        pdf.set_font("DejaVu", "B", size=10)  # Bold font for label
        pdf.cell(20, 5, txt="Email:", align="L", border=0)  # Label
        pdf.set_font("DejaVu", size=10)  # Regular font for value
        pdf.set_text_color(0, 0, 255)  # Blue color for clickable link
        pdf.cell(0, 5, txt="info@matkuling.com", align="L", ln=True, link="mailto:info@matkuling.com",
                 border=0)  # Clickable email
        pdf.set_text_color(0, 0, 0)  # Reset text color

        # Website
        pdf.set_font("DejaVu", "B", size=10)  # Bold font for label
        pdf.cell(20, 5, txt="Website:", align="L", border=0)  # Label
        pdf.set_font("DejaVu", size=10)  # Regular font for value
        pdf.set_text_color(0, 0, 255)  # Blue color for clickable link
        pdf.cell(0, 5, txt="matkuling.com", align="L", ln=True, link="https://matkuling.com",
                 border=0)  # Clickable website
        pdf.set_text_color(0, 0, 0)  # Reset text color

        # Quote Details on the right
        pdf.set_xy(150, 10)  # Move to the right side
        pdf.set_font("DejaVu", "B", size=14)  # Bold font and larger size for Quote Details title
        pdf.cell(0, 10, txt="Quote Details", align="R", ln=True)  # Title

        # Details
        pdf.set_font("DejaVu", "B", size=10)  # Bold font for labels
        pdf.cell(160, 5, txt="Reference No:", align="R", border=0)  # Label
        pdf.set_font("DejaVu", size=10)  # Regular font for value
        pdf.cell(0, 5, txt=f"{reference_number}", align="R", ln=True, border=0)  # Value
        pdf.set_font("DejaVu", "B", size=10)  # Bold font for labels
        pdf.cell(160, 5, txt="Date:", align="R", border=0)  # Label
        pdf.set_font("DejaVu", size=10)  # Regular font for value
        pdf.cell(0, 5, txt=f"{creation_date}", align="R", ln=True, border=0)  # Value
        pdf.set_font("DejaVu", "B", size=10)  # Bold font for labels
        pdf.cell(160, 5, txt="Valid Until:", align="R", border=0)  # Label
        pdf.set_font("DejaVu", size=10)  # Regular font for value
        pdf.cell(0, 5, txt=f"{valid_until_date}", align="R", ln=True, border=0)  # Value


        # Add "Quote Overview" in the middle of the table
        pdf.set_y(65)  # Set position in the center
        pdf.set_font("DejaVu", "B", size=12)  # Bold font
        pdf.cell(0, 10, txt="Quote Overview", align="C", ln=True)  # Centered text

        # Column widths and headers
        col_widths = [10, 70, 15, 20, 20, 25, 25]
        headers = ["#", "Description", "Qty", "Price", "Discount", "Discounted\nPrice", "SubTotal\nPrice"]

        # Center table horizontally
        table_width = sum(col_widths)
        pdf.set_x((210 - table_width) / 2)

        # Header row
        pdf.set_font("DejaVu", "B", size=10)  # Bold font for headers
        header_height = 12  # Increase header height for better readability
        x_start = pdf.get_x()  # Starting X position
        y_start = pdf.get_y()  # Starting Y position

        for idx, header in enumerate(headers):
            # Draw the boundary of the cell
            pdf.rect(x_start, y_start, col_widths[idx], header_height)
            # Center vertically: Calculate Y offset for vertical centering
            text_height = pdf.get_string_width(header) / col_widths[idx] * 5
            y_offset = (header_height - text_height) / 2
            # Set position and write header text
            pdf.set_xy(x_start, y_start + y_offset)
            pdf.multi_cell(col_widths[idx], 5, header, border=0, align="C")
            x_start += col_widths[idx]  # Move to the next column

        # Move cursor directly to the next row without adding unnecessary space
        pdf.set_y(y_start + header_height)

        # Add table rows
        for idx, item in enumerate(data.get("items", []), start=1):
            # Get product_name and explanation from data
            product_name = item.get('PDFOfferProductCode', 'N/A')  # Fetch product name
            explanation = item.get('PDFOfferProductExplanation', 'N/A')  # Fetch explanation

            # Calculate maximum height dynamically for row alignment
            pdf.set_font("DejaVu", size=10)
            product_name_height = len(
                pdf.multi_cell(col_widths[1], 5, product_name, border=0, align="L", split_only=True)) * 5
            pdf.set_font("DejaVu", "I", size=8)
            explanation_height = len(
                pdf.multi_cell(col_widths[1], 5, explanation, border=0, align="L", split_only=True)) * 5
            max_row_height = max(product_name_height + explanation_height, 10)

            # Draw cells
            pdf.set_x((210 - table_width) / 2)  # Center the table
            pdf.cell(col_widths[0], max_row_height, str(idx), border=1, align="C")

            # Write product_name with border
            x, y = pdf.get_x(), pdf.get_y()
            pdf.set_font("DejaVu", size=10)
            pdf.multi_cell(col_widths[1], 5, product_name, border=0, align="L")

            # Write explanation with border
            pdf.set_font("DejaVu", "I", size=8)
            pdf.set_xy(x, pdf.get_y())  # Keep explanation directly below product_name
            pdf.multi_cell(col_widths[1], 5, explanation, border=0, align="L")

            # Draw the border around the entire "Description" cell
            pdf.rect(x, y, col_widths[1], max_row_height)

            # Move to the next column
            pdf.set_xy(x + col_widths[1], y)

            # Write remaining cells with borders
            pdf.set_font("DejaVu", size=10)
            pdf.cell(col_widths[2], max_row_height, str(item.get("PDFOfferQTY", "0")), border=1, align="C")
            pdf.cell(col_widths[3], max_row_height, str(item.get("PDFOfferPrice", "0.00")), border=1, align="C")
            pdf.cell(col_widths[4], max_row_height, str(item.get("PDFOfferDiscount", "0.00")), border=1, align="C")
            pdf.cell(col_widths[5], max_row_height, str(item.get("PDFOfferDiscountedPrice", "0.00")), border=1,
                     align="C")
            pdf.cell(col_widths[6], max_row_height, str(item.get("PDFOfferSubTotal", "0.00")), border=1, align="C")
            pdf.ln(max_row_height)

        print("[DEBUG] Table rows successfully updated.")

        # Add total price
        # Check if PDFOfferPrice > 0
        # Check if PDFOfferPrice > 0
        total_price = data.get("PDFSubTotal", 0.0)

        # Varsayılan metni boş bırak
        total_price_text = ""

        # Eğer PDFOfferPrice değerlerinden biri 0'dan büyükse, metni ayarla
        if any(
                float(item.get("PDFOfferPrice", "0").replace("€", "").replace(",", ".").strip() or "0") > 0
                for item in data.get("items", [])
        ):
            total_price_text = f"Total Price: {total_price:.2f} €"

        # Text yazdırma işlemi
        pdf.ln(1)
        pdf.set_font("DejaVu", "B", size=10)
        pdf.cell(0, 10, txt=total_price_text, ln=True, align="R")


        # Save PDF
        pdf_file = os.path.join(output_folder, f"{reference_number}.pdf")
        print(f"[DEBUG] Saving PDF to: {pdf_file}")


        total_pages = pdf.page_no()  # Toplam sayfa sayısını al
        pdf.alias_nb_pages()  # Toplam sayfa sayısını FPDF'ye öğret

        pdf.set_font("DejaVu", "I", size=8)
        for page in range(1, total_pages + 1):
            footer_x = pdf.w - 10  # Sağ kenardan 40 birim içeride
            footer_y = pdf.h - 15  # Alt kenardan 10 birim yukarıda
            pdf.page = page
            pdf.set_xy(footer_x, footer_y)
            pdf.set_font("DejaVu","I", size=8)
            page_text = f"Page {page}/{total_pages}"
            print(f"[DEBUG] Writing on page {page}: {page_text}, Coordinates: ({footer_x}, {footer_y})")
            pdf.cell(0, 0, page_text, align="R")




        pdf.output(pdf_file)

        if not os.path.exists(pdf_file):
            raise FileNotFoundError(f"PDF file was not created at: {pdf_file}")

        #pdf_url = f"http://127.0.0.1:5000/static/generated_offers/{reference_number}.pdf"
        #pdf_url = f"{request.host_url}static/generated_offers/{reference_number}.pdf"
        pdf_url = f"https://apideneme.viselab.net/download-pdf/{reference_number}"

        #print(f"[DEBUG] PDF URL: {pdf_url}")
        #print(f"[DEBUG] PDF dosyası oluşturuldu: {file_path}")
        #return file_path
        #return pdf_url

        pdf.output(output_path)
        print(f"[DEBUG] PDF başarıyla oluşturuldu: {output_path}")
        return output_path





    except Exception as e:

        print(f"[ERROR] PDF oluşturma sırasında hata: {str(e)}")

        raise
