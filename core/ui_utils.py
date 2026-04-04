import streamlit as st

def inject_custom_css():
    """Injects professional Corporate Dark CSS for a premium look."""
    st.markdown("""
        <style>
        /* Main background and font */
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #1a1c24;
            border-right: 1px solid #30363d;
        }

        /* Metric cards styling */
        div[data-testid="metric-container"] {
            background-color: #1a1c24;
            border: 1px solid #30363d;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            text-align: center;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px;
            color: #8b949e;
            font-size: 16px;
            font-weight: 600;
        }

        .stTabs [aria-selected="true"] {
            color: #58a6ff !important;
            border-bottom: 2px solid #58a6ff !important;
        }

        /* Header styling */
        h1, h2, h3 {
            color: #58a6ff;
            font-weight: 700;
        }

        /* Buttons styling */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
            background-color: #21262d;
            border: 1px solid #30363d;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            border-color: #58a6ff;
            color: #58a6ff;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #1a1c24;
            border-radius: 8px;
            border: 1px solid #30363d;
        }
        </style>
    """, unsafe_allow_html=True)

def render_metric_row(cols, labels, values):
    """Helper to render a clean row of metrics."""
    for i, col in enumerate(cols):
        with col:
            st.metric(label=labels[i], value=values[i])
