import io
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class ReportService:
    @staticmethod
    def generate_html_report(data: Dict[str, Any]) -> str:
        claim_text = data.get("claim", {}).get("text", "N/A")
        verdict = data.get("verdict", {}).get("verdict", "UNVERIFIED")
        reasoning = data.get("verdict", {}).get("reasoning_summary", "")
        confidence = (data.get("confidence_score") or 0.0) * 100
        sources = data.get("sources", [])
        evidence = data.get("evidence", [])
        contradictions = data.get("contradictions", [])
        key_evidence = data.get("verdict", {}).get("key_evidence", [])
        limitations = data.get("verdict", {}).get("limitations", [])

        # Format verdict badge color
        badge_color = "#16a34a" if "TRUE" in verdict else "#dc2626" if "FALSE" in verdict else "#d97706"

        sources_html = "".join([
            f"<li><strong>{s.get('title', 'Source')}</strong> ({s.get('domain', '')}) - <a href='{s.get('url', '#')}'>{s.get('url')}</a><br/>Credibility: {s.get('evaluation', {}).get('final_credibility_score', 0.5)*100:.0f}%</li>"
            for s in sources
        ])

        evidence_html = "".join([
            f"<div style='margin-bottom: 8px; padding: 8px; background: #f8fafc; border-left: 4px solid {'#22c55e' if e.get('stance')=='SUPPORTS' else '#ef4444' if e.get('stance')=='CONTRADICTS' else '#64748b'};'>"
            f"<strong>[{e.get('stance')}]</strong> {e.get('evidence_text')}<br/>"
            f"<small style='color: #64748b;'>Source: {e.get('source', {}).get('title', 'Web Source')}</small></div>"
            for e in evidence
        ])

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8"/>
            <title>TruthLens AI Investigation Report</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #1e293b; max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
                h1 {{ font-size: 26px; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; }}
                h2 {{ font-size: 18px; color: #334155; margin-top: 24px; border-left: 4px solid #3b82f6; padding-left: 8px; }}
                .badge {{ display: inline-block; padding: 6px 14px; border-radius: 9999px; color: white; font-weight: bold; background-color: {badge_color}; }}
                .metric-card {{ background: #f1f5f9; padding: 16px; border-radius: 8px; margin-bottom: 20px; }}
                .section {{ margin-bottom: 24px; }}
            </style>
        </head>
        <body>
            <h1>TruthLens AI - Fact Verification Report</h1>
            
            <div class="metric-card">
                <p style="font-size: 18px; margin: 0 0 8px 0;"><strong>Claim:</strong> "{claim_text}"</p>
                <p style="margin: 0;"><strong>Verdict:</strong> <span class="badge">{verdict}</span> | <strong>Confidence Score:</strong> {confidence:.1f}%</p>
            </div>

            <div class="section">
                <h2>Executive Summary & Reasoning</h2>
                <p>{reasoning}</p>
            </div>

            <div class="section">
                <h2>Key Supporting & Contradicting Evidence</h2>
                {evidence_html if evidence else "<p>No evidence extracted.</p>"}
            </div>

            <div class="section">
                <h2>Key Findings & Findings Summary</h2>
                <ul>
                    {"".join([f"<li>{item}</li>" for item in key_evidence])}
                </ul>
            </div>

            <div class="section">
                <h2>Investigation Limitations</h2>
                <ul>
                    {"".join([f"<li>{item}</li>" for item in limitations])}
                </ul>
            </div>

            <div class="section">
                <h2>Evaluated Sources</h2>
                <ul>
                    {sources_html}
                </ul>
            </div>
            
            <hr style="border: 0; border-top: 1px solid #e2e8f0; margin-top: 40px;"/>
            <p style="font-size: 12px; color: #94a3b8; text-align: center;">Generated automatically by TruthLens AI Autonomous Multi-Agent Investigation System</p>
        </body>
        </html>
        """
        return html_content

    @staticmethod
    def generate_pdf_report(data: Dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=15
        )
        h2_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=12,
            spaceAfter=8
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#334155"),
            spaceAfter=8
        )

        elements = []

        # Title
        elements.append(Paragraph("TruthLens AI - Fact Verification Report", title_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#cbd5e1"), spaceAfter=15))

        # Claim & Verdict Box
        claim_text = data.get("claim", {}).get("text", "N/A")
        verdict = data.get("verdict", {}).get("verdict", "UNVERIFIED")
        confidence = (data.get("confidence_score") or 0.0) * 100

        summary_data = [
            [Paragraph(f"<b>Claim:</b> \"{claim_text}\"", body_style)],
            [Paragraph(f"<b>Verdict:</b> <font color='#16a34a'><b>{verdict}</b></font> | <b>Confidence:</b> {confidence:.1f}%", body_style)]
        ]
        t = Table(summary_data, colWidths=[540])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 15))

        # Executive Summary
        elements.append(Paragraph("Executive Summary & Reasoning", h2_style))
        reasoning = data.get("verdict", {}).get("reasoning_summary", "No reasoning summary available.")
        elements.append(Paragraph(reasoning, body_style))
        elements.append(Spacer(1, 10))

        # Evidence
        elements.append(Paragraph("Extracted Evidence Statements", h2_style))
        evidence = data.get("evidence", [])
        for e in evidence[:6]:
            stance = e.get("stance", "NEUTRAL")
            color = "#16a34a" if stance == "SUPPORTS" else "#dc2626" if stance == "CONTRADICTS" else "#475569"
            ev_p = Paragraph(f"<font color='{color}'><b>[{stance}]</b></font> {e.get('evidence_text')}", body_style)
            elements.append(ev_p)

        elements.append(Spacer(1, 15))
        elements.append(Paragraph("Generated by TruthLens AI Autonomous Multi-Agent Verification Platform", body_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
