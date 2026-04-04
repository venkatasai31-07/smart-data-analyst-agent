import streamlit as st
import pandas as pd
import os
import datetime
from dotenv import load_dotenv

from core.data_processor import DataProcessor
from core.visualization import VisualizationEngine
from core.rag_pipeline import RAGPipeline
from core.router import QueryRouter
from core.ui_utils import inject_custom_css
from core.report_generator import generate_pdf_report

# Load env variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(
    page_title="Smart Data Analyst Agent", 
    layout="wide", 
    page_icon="🤖"
)

# Apply Professional CSS
inject_custom_css()

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "processed_data" not in st.session_state:
        st.session_state.processed_data = None
    if "rag_pipeline" not in st.session_state:
        st.session_state.rag_pipeline = None
    if "insights" not in st.session_state:
        st.session_state.insights = None

def main():
    init_session_state()

    # --- SIDEBAR: ORGANIZATIONAL LOGIC ---
    with st.sidebar:
        st.title("⚙️ AI Control Center")
        
        # 📂 Section 1: Data Sources
        with st.expander("📂 DATA SOURCES", expanded=True):
            uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
            if API_KEY is None or API_KEY == "" or "your_gemini" in API_KEY:
                st.warning("⚠️ GOOGLE_API_KEY not found.")
            else:
                st.success("✅ Gemini Active")
        
        # ⚙️ Section 2: Analysis Settings
        with st.expander("⚙️ ANALYSIS CONFIG"):
            enable_cleaning = st.checkbox("Automated Data Cleaning", value=True)
            enable_rag = st.checkbox("Enable RAG Pipeline", value=True)
            model_temp = st.slider("Model Temperature", 0.0, 1.0, 0.0)

        # 🎛️ Section 3: Navigation / Quick Links
        st.markdown("---")
        st.info("💡 **Pro-Tip:** Use the 'Insights' tab for deep trend analysis.")

    # --- MAIN UI LOGIC ---
    if uploaded_file is None:
        # EMPTY STATE
        st.header("Welcome to Smart Data Analyst Agent 🤖")
        st.markdown("""
        ### Strategic Intelligence for your Datasets.
        Upload a CSV file in the sidebar to begin your analytical journey.
        
        **Available Features:**
        - 📊 **Executive Dashboard**: See the top-line numbers instantly.
        - 📈 **Visual Intelligence**: Auto-generated charts and trends.
        - 💬 **AI Agent**: Natural language conversation with your data.
        - 📑 **Record Explorer**: Deep-dive into raw data records.
        """)
        st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=1200", caption="Intelligence at Scale")
        return

    # --- FILE PROCESSING ---
    try:
        raw_df = pd.read_csv(uploaded_file)
        processor = DataProcessor(api_key=API_KEY)
        
        if st.session_state.processed_data is None:
            with st.status("🏗️ Initializing Intelligence Engine...", expanded=True) as status:
                st.write("Cleaning and normalizing data...")
                df = processor.clean_data(raw_df) if enable_cleaning else raw_df
                st.session_state.processed_data = df
                
                st.write("Generating Automated Insights...")
                st.session_state.insights = processor.generate_automated_insights(df)
                
                if enable_rag:
                    st.write("Building RAG Knowledge Base...")
                    rag = RAGPipeline(api_key=API_KEY)
                    rag.build_index(df)
                    st.session_state.rag_pipeline = rag
                
                status.update(label="✅ Analysis Ready!", state="complete", expanded=False)
        
        df = st.session_state.processed_data

        # --- TAB NAVIGATION ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Dashboard", 
            "📈 Insights Gallery", 
            "💬 AI Analyst", 
            "📑 Records"
        ])

        # 📊 TAB 1: EXECUTIVE DASHBOARD
        with tab1:
            st.header("Strategic Overview")
            
            # Metric Cards Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Rows", f"{len(df):,}")
            m2.metric("Total Columns", f"{len(df.columns)}")
            
            numeric_df = df.select_dtypes(include='number')
            if not numeric_df.empty:
                m3.metric("Avg Value (1st Num Col)", f"{numeric_df.iloc[:,0].mean():.2f}")
                m4.metric("Max Value (1st Num Col)", f"{numeric_df.iloc[:,0].max():.2f}")
            
            # Quick Actions Bar
            st.markdown("### 🚀 Quick Actions")
            qa1, qa2, qa3 = st.columns(3)
            with qa1:
                if st.button("📈 Show Trend Overview", use_container_width=True):
                    st.toast("Generating overview charts...")
                    st.session_state.last_action = "trends"
            with qa2:
                if st.button("🔍 Explain Dataset", use_container_width=True):
                    st.toast("AI is analyzing structure...")
                    st.session_state.last_action = "explain"
            with qa3:
                # Compile PDF Report data
                if st.button("📥 Generate PDF Report", use_container_width=True):
                    with st.spinner("🚀 Compiling High-Resolution Analytical PDF (This may take ~10s)..."):
                        try:
                            # Capture charts
                            all_overview_charts = VisualizationEngine.generate_overview_charts(df)
                            pdf_bytes = generate_pdf_report(df, st.session_state.insights, all_overview_charts)
                            
                            st.download_button(
                                label="💾 Download Analytical PDF",
                                data=pdf_bytes,
                                file_name=f"Analytical_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            st.success("✅ Report generated successfully!")
                        except Exception as e:
                            st.error(f"❌ Failed to generate report: {str(e)}")

            # Automated Insights Gallery
            with st.expander("🤖 AI-DRIVEN INSIGHTS SUMMARY", expanded=True):
                st.markdown(st.session_state.get("insights", "No insights found."))

        # 📈 TAB 2: INSIGHTS GALLERY
        with tab2:
            st.header("Visual Intelligence")
            overview_charts = VisualizationEngine.generate_overview_charts(df)
            for chart_name, fig in overview_charts:
                with st.container():
                    st.subheader(chart_name)
                    st.plotly_chart(fig, use_container_width=True)

        # 💬 TAB 3: AI ANALYST (AGENT)
        with tab3:
            st.header("Chat with your AI Analyst")
            
            # Query Suggestions
            st.markdown("### 💡 Suggestions")
            sug_cols = st.columns(3)
            suggestions = ["Show summary", "Top trends", "Average of numeric columns"]
            for i, sug in enumerate(suggestions):
                if sug_cols[i].button(sug, use_container_width=True):
                    # We trigger the chat input logic below manually
                    prompt = sug
            
            # Chat Display
            chat_container = st.container()
            with chat_container:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                        if "chart" in message:
                            st.plotly_chart(message["chart"], use_container_width=True)

            if chat_input := st.chat_input("Ask about your data..."):
                prompt = chat_input
                
            if 'prompt' in locals():
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                    
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing Query..."):
                        router = QueryRouter(api_key=API_KEY)
                        intent_data = router.classify_intent(prompt, list(df.columns))
                        
                        intent = intent_data.get("intent", "RAG Retrieval")
                        st.caption(f"*Engine Route: {intent}*")
                        
                        chart_to_display = None
                        response_content = ""
                        
                        if intent == "Visualization":
                            try:
                                chart_to_display = VisualizationEngine.generate_chart(df, intent_data.get("chart_type"), intent_data.get("x_col"), intent_data.get("y_col"), title=prompt)
                                response_content = f"Visualized query: **{prompt}**"
                                st.markdown(response_content)
                                st.plotly_chart(chart_to_display, use_container_width=True)
                            except Exception as e:
                                response_content = f"Visualization Error: {str(e)}"
                                st.markdown(response_content)
                                
                        elif intent == "Analytical":
                            response_content = processor.analyze_query(df, prompt)
                            st.markdown(response_content)
                        else:
                            if st.session_state.rag_pipeline:
                                rag_response = st.session_state.rag_pipeline.query(prompt)
                                response_content = rag_response.get('answer', 'Got an error')
                                st.markdown(response_content)
                            else:
                                st.warning("RAG Pipeline is disabled or initialization failed.")
                
                msg_data = {"role": "assistant", "content": response_content}
                if chart_to_display:
                    msg_data["chart"] = chart_to_display
                st.session_state.messages.append(msg_data)

        # 📑 TAB 4: RECORDS EXPLORER
        with tab4:
            st.header("Deep Record Explorer")
            st.markdown("Search and filter your raw dataset below.")
            search_term = st.text_input("🔍 Search records", "")
            
            filtered_df = df
            if search_term:
                filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
                
            st.dataframe(filtered_df, use_container_width=True)
            
            st.download_button(
                "📥 DOWNLOAD PROCESSED DATASET (CSV)",
                df.to_csv(index=False).encode('utf-8'),
                "processed_data.csv",
                "text/csv",
                key='download-csv'
            )

    except Exception as e:
        st.error(f"⚠️ **Processing Error:** {str(e)}")

if __name__ == "__main__":
    main()
