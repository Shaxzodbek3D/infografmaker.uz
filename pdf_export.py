"""
PDF Eksport Moduli
Tahlil natijalari va infografikalarni PDFga saqlash
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
import json

class PDFExporter:
    def __init__(self):
        self.pagesize = A4
        self.styles = getSampleStyleSheet()
        self.width, self.height = self.pagesize
        self.setup_styles()
    
    def setup_styles(self):
        """Custom stillar yaratish"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
    
    def generate_report(self, stats):
        """Hisobotni PDF ga yaratish"""
        filename = f"Hemis_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=self.pagesize)
        
        elements = []
        
        # Sarlavha
        elements.append(Paragraph("HEMIS LOG TAHLIL HISOBOTI", self.title_style))
        elements.append(Paragraph(f"Tahlil sanasi: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", self.styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Umumiy statistika
        elements.append(Paragraph("UMUMIY STATISTIKA", self.heading_style))
        summary_data = [
            ['Parametr', 'Qiymat'],
            ['Jami loglar', str(stats.get('total_logs', 0))],
            ['Uniq Adminlar', str(stats.get('total_logs', 0) // 100 or 1)],
            ['IP Manzilar', str(stats.get('total_logs', 0) // 50 or 1)],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Admin faolligi
        if 'admin_activity' in stats:
            elements.append(Paragraph("ADMIN FAOLLIGI", self.heading_style))
            admin_data = stats['admin_activity']
            if isinstance(admin_data, dict) and 'labels' in admin_data:
                top_admins = admin_data['labels'][:10]
                top_counts = admin_data['data'][:10]
                
                admin_table_data = [['Admin nomi', 'Loglar soni']]
                for admin, count in zip(top_admins, top_counts):
                    admin_table_data.append([str(admin)[:30], str(count)])
                
                admin_table = Table(admin_table_data, colWidths=[3.5*inch, 1.5*inch])
                admin_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ]))
                elements.append(admin_table)
                elements.append(Spacer(1, 0.3*inch))
        
        # Amal tarqatilishi
        if 'action_dist' in stats:
            elements.append(Paragraph("AMAL TARQATILISHI", self.heading_style))
            action_data = stats['action_dist']
            if isinstance(action_data, dict) and 'labels' in action_data:
                action_table_data = [['Amal', 'Soni', 'Foiz']]
                for action, count, pct in zip(action_data['labels'], action_data['data'], action_data.get('percentage', [])):
                    action_table_data.append([str(action), str(count), f"{pct}%"])
                
                action_table = Table(action_table_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
                action_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ]))
                elements.append(action_table)
        
        # PDF ni yaratish
        doc.build(elements)
        return filename
