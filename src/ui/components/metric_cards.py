import streamlit as st
from typing import List, Dict

def render_metric_cards(documents: List[Dict]):
    """
    Render high-impact analytics KPI metric cards matching design.md specifications.
    """
    total_docs = len(documents)
    flagged_docs = sum(1 for d in documents if d.get("has_validation_error"))
    
    confidences = [d.get("overall_confidence") for d in documents if d.get("overall_confidence") is not None]
    avg_conf = (sum(confidences) / len(confidences) * 100) if confidences else 0.0

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div style="background-color: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 18px 20px; text-align: left;">
                <span style="color: #94A3B8; font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Total Documents</span>
                <div style="color: #F8FAFC; font-size: 32px; font-weight: 700; margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
                    {total_docs}
                </div>
                <span style="color: #10B981; font-size: 12px; font-weight: 500;">✓ Ingested Locally</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col2:
        conf_color = "#10B981" if avg_conf >= 80 else "#F59E0B" if avg_conf >= 60 else "#EF4444"
        st.markdown(
            f"""
            <div style="background-color: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 18px 20px; text-align: left;">
                <span style="color: #94A3B8; font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Average Accuracy</span>
                <div style="color: {conf_color}; font-size: 32px; font-weight: 700; margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
                    {avg_conf:.1f}%
                </div>
                <span style="color: #94A3B8; font-size: 12px;">Model Softmax Certainty</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col3:
        flag_color = "#10B981" if flagged_docs == 0 else "#EF4444"
        badge_text = "All Verified" if flagged_docs == 0 else "Review Needed"
        st.markdown(
            f"""
            <div style="background-color: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 18px 20px; text-align: left;">
                <span style="color: #94A3B8; font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Flagged Discrepancies</span>
                <div style="color: {flag_color}; font-size: 32px; font-weight: 700; margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
                    {flagged_docs}
                </div>
                <span style="color: {flag_color}; font-size: 12px; font-weight: 500;">{badge_text}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
