import streamlit as st
import os
import sys

# Ensure imports work when running from root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ui.styles import inject_custom_css
from src.ui.components.canvas_overlay import render_bounding_boxes
from src.ui.components.field_editor import render_field_editor
from src.ui.components.metric_cards import render_metric_cards
from src.ui.utils import upload_document, fetch_documents, API_BASE_URL

st.set_page_config(page_title="DocuParse AI", page_icon="📄", layout="wide")
inject_custom_css()

def main():
    st.title("📄 DocuParse AI")
    st.markdown("Intelligent Document Understanding for Financial Records")
    
    tab1, tab2, tab3 = st.tabs(["Upload & Process", "Review Workspace", "Analytics & Export"])
    
    with tab1:
        st.subheader("Ingest Documents")
        uploaded_file = st.file_uploader(
            "Drag and drop your invoice or receipt here", 
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="Supported formats: PNG, JPG, JPEG, and PDF up to 10MB."
        )
        
        if uploaded_file is not None:
            if st.button("Process Document", use_container_width=True, type="primary"):
                with st.spinner("Extracting tokens, analyzing layout, and validating rules..."):
                    try:
                        doc = upload_document(uploaded_file)
                        st.session_state["current_doc"] = doc
                        st.success("Document processed successfully! Switch to the Review Workspace tab to verify.")
                    except Exception as e:
                        st.error(f"Processing failed: {e}")
                        
    with tab2:
        doc = st.session_state.get("current_doc")
        if not doc:
            st.info("Upload and process a document in the 'Upload & Process' tab to begin review.")
        else:
            st.subheader(f"Reviewing: {doc['original_filename']}")
            
            if doc.get('has_validation_error'):
                st.warning("⚠️ Arithmetic Warning: Subtotal + Tax does not match Total within tolerance ($0.05). Please verify fields below.")
                
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### Document View & Bounding Boxes")
                img = render_bounding_boxes(doc['file_path'], doc.get('extractions', []))
                st.image(img, use_container_width=True)
                
            with col2:
                render_field_editor(doc['id'], doc.get('extractions', []))
                
    with tab3:
        st.subheader("System Analytics & Records")
        
        try:
            docs = fetch_documents(limit=100)
            if docs:
                render_metric_cards(docs)
                
                st.markdown("### Processed Document Records")
                for d in docs[:10]:
                    conf = d.get('overall_confidence')
                    conf_str = f" • Confidence: {conf * 100:.1f}%" if conf else ""
                    with st.expander(f"📄 {d['original_filename']} — [{d['status']}]{conf_str}"):
                        st.write(f"**Document ID:** `{d['id']}`")
                        st.write(f"**Uploaded:** {d['uploaded_at']}")
                        
                        btn_c1, btn_c2 = st.columns([1, 1])
                        with btn_c1:
                            st.markdown(f"📥 [Download CSV Export]({API_BASE_URL}/documents/{d['id']}/export?format=csv)")
                        with btn_c2:
                            st.markdown(f"📋 [Download JSON Export]({API_BASE_URL}/documents/{d['id']}/export?format=json)")
            else:
                st.info("No documents have been ingested yet. Ingest your first document to see metrics!")
        except Exception as e:
            st.error(f"Could not load analytics: {e}. Ensure the FastAPI server is running on port 8000.")

if __name__ == "__main__":
    main()
