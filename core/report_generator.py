from fpdf import FPDF
import io
import pandas as pd
import datetime
import re

class ReportGenerator(FPDF):
    def header(self):
        # Professional Header with logo placement (if any) and title
        self.set_font('Helvetica', 'B', 15)
        self.set_text_color(88, 166, 255)  # Cyan/Blue color
        self.cell(0, 10, 'Smart Data Analyst Agent - Executive Report', 0, 1, 'C')
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        # Footer with page numbers
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def add_section_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(31, 119, 180)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def add_metric_box(self, label, value):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(0, 0, 0)
        self.cell(40, 7, f"{label}: ", 0, 0)
        self.set_font('Helvetica', '', 10)
        self.cell(0, 7, str(value), 0, 1)

    def add_text_block(self, text):
        self.set_font('Helvetica', '', 11)
        self.set_text_color(33, 37, 41)
        # Strip any emojis or special characters not supported by Helvetica
        safe_text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        self.multi_cell(0, 6, safe_text)
        self.ln(5)

def generate_pdf_report(df, insights, charts):
    """
    df: Pandas DataFrame
    insights: AI insights string
    charts: List of (chart_name, fig) tuples from VisualizationEngine.generate_overview_charts
    """
    pdf = ReportGenerator()
    pdf.add_page()
    
    # --- 📊 SECTION 1: TOP METRICS ---
    pdf.add_section_title("1. Executive Summary")
    pdf.add_metric_box("Total Records", len(df))
    pdf.add_metric_box("Total Columns", len(df.columns))
    
    numeric_df = df.select_dtypes(include='number')
    if not numeric_df.empty:
        pdf.add_metric_box("Mean Analysis", f"{numeric_df.iloc[:,0].mean():.2f}")
    pdf.ln(5)

    # --- 🤖 SECTION 2: AI INSIGHTS ---
    pdf.add_section_title("2. AI Intelligence Engine Insights")
    # Clean the insights text slightly (remove markdown symbols)
    clean_insights = insights.replace('**', '').replace('###', '').replace('- ', '• ')
    pdf.add_text_block(clean_insights)
    pdf.add_page()

    # --- 📈 SECTION 3: VISUAL INTELLIGENCE ---
    pdf.add_section_title("3. Visual Insights Gallery")
    pdf.ln(5)

    for chart_name, fig in charts:
        try:
            # Convert Plotly figure to PNG bytes using kaleido
            img_bytes = fig.to_image(format="png", width=700, height=450, scale=2)
            img_stream = io.BytesIO(img_bytes)
            
            # Add to PDF
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 10, f"Chart: {chart_name}", 0, 1, 'L')
            pdf.image(img_stream, w=180)
            pdf.ln(10)
        except Exception as e:
            pdf.set_font('Helvetica', 'I', 10)
            pdf.set_text_color(255, 0, 0)
            pdf.cell(0, 10, f"Error rendering chart {chart_name}: {str(e)}", 0, 1)
            pdf.set_text_color(0,0,0)

    # Return PDF as bytes
    return bytes(pdf.output())
