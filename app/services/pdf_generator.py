import logging
from typing import List, Dict, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFGeneratorService:
    """Service for generating PDF summaries"""
    
    def __init__(self, output_directory: str = "./downloads"):
        """Initialize PDF generator"""
        self.output_directory = output_directory
        os.makedirs(output_directory, exist_ok=True)
    
    def generate_summary_pdf(
        self,
        title: str,
        summary: str,
        metadata: Dict,
        key_findings: Optional[List[str]] = None,
        insights: Optional[List[str]] = None,
        user_id: int = None,
        paper_id: int = None
    ) -> str:
        """Generate PDF document with summary"""
        try:
            filename = f"summary_{paper_id}_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.output_directory, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=letter,
                                   rightMargin=0.75*inch,
                                   leftMargin=0.75*inch,
                                   topMargin=0.75*inch,
                                   bottomMargin=0.75*inch)
            
            story = []
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=30,
                alignment=1  # center
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Add title
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Add metadata
            story.append(Paragraph("Document Metadata", heading_style))
            metadata_data = [
                ['Metric', 'Value'],
                ['File Size', f"{metadata.get('file_size_mb', 0):.2f} MB"],
                ['Word Count', f"{metadata.get('words', 0):,}"],
                ['Processing Time', f"{metadata.get('processing_time', 0):.2f}s"],
                ['Chunks Count', str(metadata.get('chunks_count', 0))],
                ['Generation Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            ]
            
            metadata_table = Table(metadata_data)
            metadata_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(metadata_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Add summary
            story.append(Paragraph("Summary", heading_style))
            story.append(Paragraph(summary, styles['BodyText']))
            story.append(Spacer(1, 0.3*inch))
            
            # Add key findings if available
            if key_findings:
                story.append(Paragraph("Key Findings", heading_style))
                for i, finding in enumerate(key_findings, 1):
                    story.append(Paragraph(f"• {finding}", styles['BodyText']))
                story.append(Spacer(1, 0.3*inch))
            
            # Add insights if available
            if insights:
                story.append(Paragraph("Insights", heading_style))
                for i, insight in enumerate(insights, 1):
                    story.append(Paragraph(f"• {insight}", styles['BodyText']))
            
            # Build PDF
            doc.build(story)
            logger.info(f"PDF generated: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise
    
    def get_download_url(self, filepath: str) -> str:
        """Get download URL for generated PDF"""
        filename = os.path.basename(filepath)
        return f"/downloads/{filename}"
