from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf_report(df, response):
    """
    Generates a PDF report using only selected columns.
    """
    doc = SimpleDocTemplate(response, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()
    
    # Convert DataFrame to list of lists
    table_data = [df.columns.tolist()] + df.values.tolist()

    # Add Title
    elements.append(Paragraph("Drone Log Report", styles["Title"]))

    # Paginate Large Data
    max_rows_per_page = 20  
    for i in range(0, len(table_data), max_rows_per_page):
        table_slice = table_data[i:i + max_rows_per_page]
        column_widths = [100] * len(df.columns)  

        # Create Table
        table = Table(table_slice, colWidths=column_widths)

        # Apply Styles
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(style)

        elements.append(table)
        
        # Add Page Break if more data is left
        if i + max_rows_per_page < len(table_data):
            elements.append(PageBreak())

    # Build PDF
    doc.build(elements)
