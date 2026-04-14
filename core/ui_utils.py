import streamlit as st

def inject_custom_css():
    """Injects a clean, SaaS-grade Streamlit UI for professional product feel."""
    st.markdown("""
        <style>
        /* Main background */
        .stApp {
            background-color: #0e1117;
            color: #f8fafc;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #1a1c24;
            border-right: 1px solid rgba(255,255,255,0.05);
        }

        /* Metric cards styling: Keep subtle card styling */
        div[data-testid="metric-container"] {
            background: #161821;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 12px;
            padding: 16px;
            text-align: left;
            transition: all 0.2s ease;
        }

        /* Smooth hover (very subtle) */
        div[data-testid="metric-container"]:hover {
            border-color: rgba(100,150,255,0.25);
        }

        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 600;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 48px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px;
            color: #8b949e;
            font-size: 16px;
            font-weight: 500;
        }

        .stTabs [aria-selected="true"] {
            color: #cbd5e1 !important;
            border-bottom: 2px solid #3b82f6 !important;
        }

        /* Header styling (cleaner) */
        h1, h2, h3 {
            color: #f8fafc;
            font-weight: 600;
        }

        /* Buttons styling */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
            background-color: #1f232d;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            border-color: rgba(100,150,255,0.4);
            color: #cbd5e1;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #161821;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        
        /* Chat Styling */
        .stChatMessage {
            background: #1a1c24 !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
            border-radius: 8px !important;
            margin-bottom: 1rem;
        }

        </style>
    """, unsafe_allow_html=True)

def render_metric_row(cols, labels, values):
    """Helper to render a clean row of metrics."""
    for i, col in enumerate(cols):
        with col:
            st.metric(label=labels[i], value=values[i])
