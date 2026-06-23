"""PDF report generator — creates a downloadable financial summary PDF using ReportLab."""

import io
import logging
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)

logger = logging.getLogger(__name__)

# Color palette
PRIMARY = HexColor("#1a73e8")
HEADER_BG = HexColor("#1a73e8")
ROW_BG = HexColor("#f8f9fa")
SEVERITY_COLORS = {
    "info": HexColor("#34a853"),
    "warning": HexColor("#fbbc04"),
    "critical": HexColor("#ea4335"),
}


class ReportGenerator:
    """Generate a PDF financial summary report from processed statement data."""

    def generate_pdf(
        self,
        statement_id: str,
        filename: str,
        metrics: dict,
        recurring_items: list[dict] = None,
        insights: list[dict] = None,
    ) -> bytes:
        """Generate a PDF report as bytes.
        
        Returns the PDF binary content for download.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=PRIMARY,
            spaceAfter=6,
        ))
        styles.add(ParagraphStyle(
            name="MetricValue",
            parent=styles["Normal"],
            fontSize=12,
            textColor=black,
        ))

        story = []

        # Title
        story.append(Paragraph("RupeeRadar — Financial Summary Report", styles["Title"]))
        story.append(Paragraph(f"Statement: {filename}", styles["Normal"]))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
        story.append(Spacer(1, 12))

        # Metrics Summary
        story.append(Paragraph("Financial Overview", styles["SectionTitle"]))
        metrics_data = [
            ["Metric", "Value"],
            ["Total Income", f"₹{metrics.get('total_income', 0):,.2f}"],
            ["Total Spend", f"₹{metrics.get('total_spend', 0):,.2f}"],
            ["Savings", f"₹{metrics.get('savings', 0):,.2f}"],
            ["Savings Rate", f"{metrics.get('savings_rate', 0) or 0:.1f}%"],
        ]
        metrics_table = Table(metrics_data, colWidths=[200, 200])
        metrics_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#dee2e6")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, ROW_BG]),
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 12))

        # Category Breakdown
        story.append(Paragraph("Spending by Category", styles["SectionTitle"]))
        top_cats = metrics.get("top_categories", [])
        if top_cats:
            cat_data = [["Category", "Amount", "Transactions", "% of Spend"]]
            for c in top_cats:
                cat_data.append([c["name"], f"₹{c['total']:,.2f}", str(c["count"]), f"{c['percentage']}%"])
            cat_table = Table(cat_data, colWidths=[120, 120, 80, 80])
            cat_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("ALIGN", (3, 0), (3, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#dee2e6")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, ROW_BG]),
            ]))
            story.append(cat_table)
        else:
            story.append(Paragraph("No spending data available.", styles["Normal"]))
        story.append(Spacer(1, 12))

        # Recurring Payments
        story.append(Paragraph("Recurring Payments", styles["SectionTitle"]))
        if recurring_items:
            rec_data = [["Merchant", "Amount", "Frequency", "Annual Cost"]]
            for r in recurring_items:
                next_date = r.get("next_expected_date", "N/A")
                if hasattr(next_date, "strftime"):
                    next_date = next_date.strftime("%Y-%m-%d")
                rec_data.append([r["merchant"], f"₹{abs(r['amount']):,.2f}", r["frequency"], f"₹{r['annual_cost']:,.2f}"])
            rec_table = Table(rec_data, colWidths=[120, 100, 80, 100])
            rec_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("ALIGN", (3, 0), (3, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#dee2e6")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, ROW_BG]),
            ]))
            story.append(rec_table)
        else:
            story.append(Paragraph("No recurring payments detected.", styles["Normal"]))
        story.append(Spacer(1, 12))

        # Insights
        story.append(Paragraph("AI-Generated Insights", styles["SectionTitle"]))
        if insights:
            for insight in insights:
                severity = insight.get("severity", "info")
                color = SEVERITY_COLORS.get(severity, SEVERITY_COLORS["info"])
                badge = f'<font color="{color.hexval()}">[{severity.upper()}]</font>'
                story.append(Paragraph(f"{badge} {insight.get('title', '')}", styles["Normal"]))
                story.append(Paragraph(f"  {insight.get('description', '')}", styles["Normal"]))
                if insight.get("amount_referenced"):
                    story.append(Paragraph(f"  Amount referenced: ₹{insight['amount_referenced']:,.2f}", styles["Normal"]))
                story.append(Spacer(1, 4))
        else:
            story.append(Paragraph("No insights generated.", styles["Normal"]))

        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(f"Generated PDF report for statement {statement_id}: {len(pdf_bytes)} bytes")
        return pdf_bytes
