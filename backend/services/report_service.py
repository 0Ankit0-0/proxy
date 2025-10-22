from pathlib import Path
from datetime import datetime
import pandas as pd
import json
from typing import Dict, List
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

class ReportGenerator:
    """Generate analysis reports in multiple formats"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path.cwd() / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
    
    def generate_csv_report(self, data: List[Dict], filename: str = None) -> Path:
        """
        Generate CSV report from query results
        
        Args:
            data: List of dictionaries containing log data
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to generated CSV file
        """
        if not filename:
            filename = f"log_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output_path = self.output_dir / filename
        
        # Convert to DataFrame and export
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        return output_path
    
    def generate_json_report(self, data: Dict, filename: str = None) -> Path:
        """Generate JSON report"""
        if not filename:
            filename = f"log_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return output_path
    
    def generate_pdf_report(
        self, 
        title: str,
        summary: Dict,
        anomalies: List[Dict],
        statistics: Dict,
        filename: str = None
    ) -> Path:
        """
        Generate comprehensive PDF report
        
        Args:
            title: Report title
            summary: Summary statistics
            anomalies: List of detected anomalies
            statistics: Database statistics
            filename: Output filename
        
        Returns:
            Path to generated PDF
        """
        if not filename:
            filename = f"security_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        output_path = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for PDF elements
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Report metadata
        metadata_text = f"""
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Project:</b> Quorum - Offline Log Intelligence Platform<br/>
        <b>Analysis Period:</b> {summary.get('start_time', 'N/A')} to {summary.get('end_time', 'N/A')}
        """
        story.append(Paragraph(metadata_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Executive Summary
        story.append(Paragraph("<b>Executive Summary</b>", self.styles['Heading2']))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Logs Analyzed', f"{statistics.get('total_logs', 0):,}"],
            ['Anomalies Detected', f"{statistics.get('anomalies', 0):,}"],
            ['Unique Hosts', f"{statistics.get('unique_hosts', 0):,}"],
            ['Anomaly Rate', f"{(statistics.get('anomalies', 0) / max(statistics.get('total_logs', 1), 1) * 100):.2f}%"],
            ['Average Anomaly Score', f"{statistics.get('avg_anomaly_score', 0):.4f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Top Anomalies
        story.append(PageBreak())
        story.append(Paragraph("<b>Top Detected Anomalies</b>", self.styles['Heading2']))
        story.append(Spacer(1, 0.1 * inch))
        
        if anomalies:
            for i, anomaly in enumerate(anomalies[:20], 1):  # Top 20
                anomaly_text = f"""
                <b>Anomaly #{i}</b> (Score: {anomaly.get('score', 0):.4f})<br/>
                <b>Timestamp:</b> {anomaly.get('timestamp', 'N/A')}<br/>
                <b>Host:</b> {anomaly.get('host', 'Unknown')}<br/>
                <b>Message:</b> {anomaly.get('message', 'N/A')[:200]}...<br/>
                """
                story.append(Paragraph(anomaly_text, self.styles['Normal']))
                story.append(Spacer(1, 0.15 * inch))
        else:
            story.append(Paragraph("No anomalies detected.", self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return output_path


# Add routes in backend/routes/reports.py (NEW FILE)

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.report_service import ReportGenerator
from services.storage_service import StorageService
from config import DATA_DIR

router = APIRouter()
report_gen = ReportGenerator(output_dir=DATA_DIR / "reports")

@router.get("/export/csv")
async def export_csv_report(query: str = "SELECT * FROM logs WHERE is_anomaly = TRUE"):
    """Export query results to CSV"""
    try:
        result = StorageService.query_logs(query)
        
        # Convert to list of dicts
        data = [
            {
                "timestamp": row[0],
                "host": row[1],
                "message": row[2],
                "anomaly_score": row[3]
            }
            for row in result
        ]
        
        csv_path = report_gen.generate_csv_report(data)
        
        return FileResponse(
            path=str(csv_path),
            filename=csv_path.name,
            media_type='text/csv'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/pdf")
async def export_pdf_report():
    """Generate comprehensive PDF analysis report"""
    try:
        # Get statistics
        stats = StorageService.get_statistics()
        
        # Get top anomalies
        anomaly_results = StorageService.query_logs(
            "SELECT timestamp, host, message, anomaly_score FROM logs WHERE is_anomaly = TRUE ORDER BY anomaly_score DESC LIMIT 50"
        )
        
        anomalies = [
            {
                "timestamp": row[0],
                "host": row[1],
                "message": row[2],
                "score": row[3]
            }
            for row in anomaly_results
        ]
        
        summary = {
            "start_time": stats.get('earliest_log', 'N/A'),
            "end_time": stats.get('latest_log', 'N/A')
        }
        
        pdf_path = report_gen.generate_pdf_report(
            title="Project Quorum - Security Analysis Report",
            summary=summary,
            anomalies=anomalies,
            statistics=stats
        )
        
        return FileResponse(
            path=str(pdf_path),
            filename=pdf_path.name,
            media_type='application/pdf'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update backend/app.py to include this router:
# from routes import reports
# app.include_router(reports.router, prefix="/reports", tags=["Reports"])