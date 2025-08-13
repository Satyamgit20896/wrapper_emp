from flask import Flask, request, jsonify, url_for
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from openpyxl import Workbook
import os
from datetime import datetime

app = Flask(__name__)

PDF_FOLDER = 'static/pdfs'
EXCEL_FOLDER = 'static/excels'
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(EXCEL_FOLDER, exist_ok=True)

@app.route('/convert-text-to-pdf', methods=['POST'])
def convert_text_to_pdf():
    data = request.get_json()
    rows = data.get('data', [])

    if not rows or not isinstance(rows, list):
        return {"error": "Invalid or missing 'data' list"}, 400

    # Generate timestamped filenames
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    pdf_filename = f"structured_output_{timestamp}.pdf"
    excel_filename = f"structured_output_{timestamp}.xlsx"
    pdf_path = os.path.join(PDF_FOLDER, pdf_filename)
    excel_path = os.path.join(EXCEL_FOLDER, excel_filename)

    # 📄 Generate PDF
    table_data = [["Field", "Value"]] + [[r.get("Field", ""), r.get("Value", "")] for r in rows]
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    table = Table(table_data, colWidths=[200, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))
    doc.build([table])

    # 📊 Generate Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Structured Data"
    ws.append(["Field", "Value"])
    for row in rows:
        ws.append([row.get("Field", ""), row.get("Value", "")])
    wb.save(excel_path)

    # 🔗 Generate URLs
    pdf_url = url_for('static', filename=f'pdfs/{pdf_filename}', _external=True)
    excel_url = url_for('static', filename=f'excels/{excel_filename}', _external=True)

    return jsonify({
        "message": "PDF and Excel generated successfully",
        "pdf_url": pdf_url,
        "excel_url": excel_url
    })

if __name__ == '__main__':
    app.run(debug=True)
