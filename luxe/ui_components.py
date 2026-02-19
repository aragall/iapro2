import streamlit as st

def setup_page():
    """Sets up the page configuration and custom Corporate CSS."""
    st.set_page_config(
        page_title="AURA FINANCE | Institutional",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for Institutional Financial Look
    custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

        /* General Body and Background */
        .stApp {
            background-color: #0d1117; /* Deepest Corporate Navy/Black */
            color: #C9D1D9; /* Off-white text */
            font-family: 'Inter', sans-serif;
            font-size: 14px;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #010409; /* Darker than main */
            border-right: 1px solid #30363d;
        }
        
        /* Sidebar Nav Items */
        .stRadio > div[role="radiogroup"] > label {
            background-color: transparent !important;
            border: none;
            color: #8b949e;
            font-weight: 500;
            padding: 8px 12px;
            transition: color 0.2s;
        }
        
        .stRadio > div[role="radiogroup"] > label:hover {
            color: #58a6ff; /* Corporate Blue hover */
        }

        /* Headers */
        h1, h2, h3 {
            color: #F0F6FC;
            font-weight: 600;
            letter-spacing: -0.3px;
        }
        h1 { font-size: 26px; border-bottom: 1px solid #21262d; padding-bottom: 10px; }
        h2 { font-size: 20px; margin-top: 20px; }
        h3 { font-size: 16px; color: #8b949e; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
        
        /* Metric Cards (Bloomberg Style) */
        .metric-container {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 4px; /* Sharp corners */
            padding: 15px;
            margin-bottom: 10px;
        }
        
        .metric-label {
            font-size: 12px;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: 500;
            color: #F0F6FC;
            letter-spacing: -0.5px;
        }
        
        .metric-delta {
            font-size: 12px;
            margin-left: 8px;
        }
        
        .delta-pos { color: #3fb950; } /* Green */
        .delta-neg { color: #f85149; } /* Red */
        
        /* Buttons (Professional) */
        .stButton > button {
            background-color: #238636; /* Institutional Green */
            color: #ffffff;
            border: 1px solid rgba(240,246,252,0.1);
            border-radius: 4px;
            padding: 6px 16px;
            font-weight: 500;
            font-size: 13px;
            transition: background-color 0.2s;
        }
        
        .stButton > button:hover {
            background-color: #2ea043;
            border-color: rgba(240,246,252,0.1);
        }
        
        /* Secondary Button (Outline) */
        .stButton > button.secondary {
            background-color: transparent;
            border: 1px solid #30363d;
            color: #c9d1d9;
        }

        /* Inputs */
        .stTextInput > div > div > input {
            background-color: #0d1117;
            color: #c9d1d9;
            border: 1px solid #30363d;
            border-radius: 4px;
            font-size: 13px;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #58a6ff;
            box-shadow: 0 0 0 1px #58a6ff;
        }

        /* Dataframes / Tables */
        [data-testid="stDataFrame"] {
            font-family: 'Inter', monospace;
            font-size: 12px;
        }
        
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def metric_card(label, value, delta=None, delta_color="normal"):
    """Renders a corporate metric card."""
    delta_html = ""
    if delta:
        color_class = "delta-pos" if "+" in delta else "delta-neg"
        delta_html = f"<span class='metric-delta {color_class}'>{delta}</span>"
        
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value} {delta_html}</div>
    </div>
    """, unsafe_allow_html=True)

def section_header(title, subtitle=None):
    """Renders a styled section header."""
    st.markdown(f"## {title}")
    if subtitle:
        st.markdown(f"<div style='color: #8b949e; font-size: 13px; margin-top: -10px; margin-bottom: 20px;'>{subtitle}</div>", unsafe_allow_html=True)

