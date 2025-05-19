from flask import Flask, render_template, request, send_file
import os
from PyPDF2 import PdfReader, PdfWriter
import re

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['pdf']
        if file:
            filename = file.filename.replace(" ", "_")
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            output_path = os.path.join(UPLOAD_FOLDER, f"sorted_{filename}")
            
            file.save(input_path)
            print("✅ File uploaded to:", input_path)

            sort_pdf(input_path, output_path)

            # 🔍 Check if sorted file created
            if not os.path.exists(output_path):
                print("❌ Output file not created:", output_path)
                return "Error: Sorted PDF not generated."

            print("✅ Sorted file ready:", output_path)
            return send_file(output_path, as_attachment=True)

    return render_template('index.html')

def sort_pdf(input_pdf, output_pdf):
    print("🛠️ Sorting PDF started")
    reader = PdfReader(input_pdf)
    product_page_map = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        lines = text.splitlines()
        product_name = "UNKNOWN"
        for idx, line in enumerate(lines):
            if "SKU Item Name" in line:
                product_lines = []
                for j in range(1, 4):
                    if idx + j < len(lines):
                        pline = lines[idx + j].strip()
                        if re.match(r"^\d+\s+\d+$", pline) or re.match(r"^Order Total", pline):
                            break
                        product_lines.append(pline)
                product_name = " ".join(product_lines).strip()
                break
        print(f"🔍 Found product on page {i + 1}: {product_name}")
        product_page_map.append((product_name, i))

    product_page_map.sort(key=lambda x: x[0].lower())
    writer = PdfWriter()
    for _, page_index in product_page_map:
        writer.add_page(reader.pages[page_index])

    with open(output_pdf, "wb") as f:
        writer.write(f)
    print("✅ Sorted PDF written to:", output_pdf)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
