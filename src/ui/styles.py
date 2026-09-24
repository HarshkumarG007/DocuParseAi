import streamlit as st

def inject_custom_css():
    st.markdown(
        """
        <style>
        /* Base Dark Theme Overrides */
        :root {
            --primary-bg: #0A0A0B;
            --surface-bg: #1A1A1E;
            --accent-glow: #6366F1;
            --text-main: #FFFFFF;
            --text-muted: #8B8B9E;
            --border-subtle: #2D2D35;
            --success-color: #10B981;
            --warning-color: #F59E0B;
            --error-color: #EF4444;
        }
        
        /* Typography */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: var(--accent-glow) !important;
            color: white !important;
            border-radius: 6px !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        .stButton>button:hover {
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.4) !important;
            transform: translateY(-1px) !important;
        }
        
        /* File Uploader */
        div[data-testid="stFileUploader"] > section {
            border: 2px dashed var(--border-subtle);
            border-radius: 12px;
            background-color: rgba(26, 26, 30, 0.5);
            backdrop-filter: blur(10px);
        }
        
        /* Metrics & Cards */
        div[data-testid="metric-container"] {
            background-color: var(--surface-bg);
            border: 1px solid var(--border-subtle);
            padding: 1rem;
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
