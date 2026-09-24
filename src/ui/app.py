import streamlit as st
import requests
import os
import sys

# Ensure imports work when running from root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ui.styles import inject_custom_css
from src.ui.components.canvas_overlay import render_bounding_boxes
from src.ui.components.field_editor import render_field_editor

API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="DocuParse AI", page_icon="📄", layout="wide")
inject_custom_css()

def main():
    st.title("📄 DocuParse AI")
    st.markdown("Intelligent Document Understanding for Financial Records")
    
    tab1, tab2, tab3 = st.tabs(["Upload & Process", "Review Workspace", "Analytics & Export"])
    
    with tab1:
        st.subheader("Ingest Documents")
        uploaded_file = st.file_uploader("Drag and drop your invoice or receipt here", type=['png', 'jpg', 'jpeg', 'pdf'])
        
        if uploaded_file is not None:
            if st.button("Process Document", use_container_width=True):
                with st.spinner("Extracting tokens, analyzing layout, and validating rules..."):
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    try:
                        res = requests.post(f"{API_URL}/documents/upload", files=files)
                        if res.status_code == 201:
                            st.session_state["current_doc"] = res.json()
                            st.success("Document processed successfully! Switch to the Review Workspace tab.")
                        else:
                            st.error(f"Error: {res.text}")
                    except Exception as e:
                        st.error(f"Failed to connect to backend: {e}. Is the FastAPI server running?")
                        
    with tab2:
        doc = st.session_state.get("current_doc")
        if not doc:
            st.info("Upload and process a document first to see it here.")
        else:
            st.subheader(f"Reviewing: {doc['original_filename']}")
            
            if doc.get('has_validation_error'):
                st.warning("⚠️ This document has validation warnings (e.g. Math Discrepancy). Please review carefully.")
                
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### Document View")
                # Render bounding boxes
                img = render_bounding_boxes(doc['file_path'], doc.get('extractions', []))
                st.image(img, use_container_width=True)
                
            with col2:
                render_field_editor(doc['id'], doc.get('extractions', []))
                
    with tab3:
        st.subheader("System Analytics")
        if st.button("Refresh Analytics"):
            try:
                res = requests.get(f"{API_URL}/documents?limit=100")
                if res.status_code == 200:
                    docs = res.json()
                    
                    # Metrics
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Total Documents Processed", len(docs))
                    errors = sum(1 for d in docs if d.get("has_validation_error"))
                    m2.metric("Documents Requiring Review", errors)
                    
                    # Simple table
                    if docs:
                        st.markdown("### Recent Documents")
                        for d in docs[:5]:
                            with st.expander(f"{d['original_filename']} - {d['status']}"):
                                st.write(f"Uploaded: {d['uploaded_at']}")
                                st.markdown(f"[Download CSV Export]({API_URL}/documents/{d['id']}/export?format=csv)")
                                st.markdown(f"[Download JSON Export]({API_URL}/documents/{d['id']}/export?format=json)")
            except:
                st.error("Backend not reachable. Cannot load analytics.")

if __name__ == "__main__":
    main()
