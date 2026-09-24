import streamlit as st
import requests

API_URL = "http://localhost:8000/api/v1"

def render_field_editor(doc_id: str, extractions: list):
    """Render editable fields for the document with API correction syncing."""
    st.markdown("### Extracted Data")
    
    for ext in extractions:
        field_type = ext["field_type"].capitalize()
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown(f"**{field_type}**")
            
        with col2:
            key = f"input_{ext['id']}"
            new_val = st.text_input(
                "Value", 
                value=ext.get("normalized_text") or ext.get("raw_text", ""),
                key=key,
                label_visibility="collapsed"
            )
            
        with col3:
            conf = ext["confidence"] * 100
            color = "green" if conf > 80 else "orange" if conf > 50 else "red"
            st.markdown(f"<span style='color:{color}; font-size:12px;'>{conf:.1f}% Conf</span>", unsafe_allow_html=True)
            
            # If value changed, show save button
            original = ext.get("normalized_text") or ext.get("raw_text", "")
            if new_val != original:
                if st.button("Save", key=f"btn_{ext['id']}"):
                    payload = {
                        "field_type": ext["field_type"],
                        "original_value": original,
                        "corrected_value": new_val
                    }
                    try:
                        res = requests.post(f"{API_URL}/documents/{doc_id}/correct", json=payload)
                        if res.status_code == 200:
                            st.success("Saved!")
                            # In a real app we'd refresh state here, simplified for MVP
                    except Exception as e:
                        st.error("Failed to connect to API.")
