from flask import Flask, request, send_from_directory, jsonify
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import os
import uuid
import openpyxl

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Increased to 10MB for large payloads

# Folders for storing files
PDF_FOLDER = "pdfs"
EXCEL_FOLDER = "excels"
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(EXCEL_FOLDER, exist_ok=True)


@app.route('/generate-files', methods=['POST'])
def generate_files():
    try:
        req_json = request.get_json()
        data = req_json.get("data", [])

        if not isinstance(data, list) or not data:
            return jsonify({"error": "Invalid data format. 'data' must be a non-empty list of dictionaries."}), 400

        headers = list(data[0].keys())

        # ---------- PDF ----------
        pdf_filename = f"{uuid.uuid4()}.pdf"
        pdf_path = os.path.join(PDF_FOLDER, pdf_filename)

        pdf = SimpleDocTemplate(
            pdf_path,
            pagesize=landscape(letter),
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=20
        )

        table_data = [headers] + [[str(item.get(h, "")) for h in headers] for item in data]
        table = Table(table_data, repeatRows=1)

        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),  # Smaller font for more rows
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black)
        ])
        table.setStyle(style)

        pdf.build([table])  # Automatically paginates if table is too long

        # ---------- Excel ----------
        excel_filename = f"{uuid.uuid4()}.xlsx"
        excel_path = os.path.join(EXCEL_FOLDER, excel_filename)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(headers)
        for item in data:
            ws.append([item.get(h, "") for h in headers])

        for col in ws.columns:
            max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_length + 2

        wb.save(excel_path)

        return jsonify({
            "pdf_url": f"{request.url_root}download-pdf/{pdf_filename}",
            "excel_url": f"{request.url_root}download-excel/{excel_filename}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download-pdf/<filename>', methods=['GET'])
def download_pdf(filename):
    return send_from_directory(PDF_FOLDER, filename, as_attachment=True)


@app.route('/download-excel/<filename>', methods=['GET'])
def download_excel(filename):
    return send_from_directory(EXCEL_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
