import streamlit as st
import httpx
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings

st.set_page_config(
    page_title="TrafficLawBot",
    page_icon="🚦",
    layout="wide"
)

st.title("🚦 TrafficLawBot: Indian Traffic Rules Assistant")
st.caption("Ask about traffic laws, fines, and challans (Telangana/Hyderabad focus)")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("📚 Sources"):
                for src in message["sources"]:
                    st.markdown(f"**Source {src['id']}** (score: {src['score']:.3f})")
                    st.text(src["text"])
                    st.json(src["metadata"])

# Chat input
if prompt := st.chat_input("Ask about traffic rules, fines, or challans..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from API
    with st.chat_message("assistant"):
        with st.spinner("Searching traffic laws..."):
            try:
                response = httpx.post(
                    f"http://localhost:{settings.api_port}/ask",
                    json={"question": prompt},
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                st.markdown(result["answer"])
                
                # Show confidence
                confidence_color = {
                    "high": "🟢",
                    "medium": "🟡",
                    "low": "🔴"
                }
                st.caption(f"Confidence: {confidence_color.get(result['confidence'], '⚪')} {result['confidence']}")
                
                # Sources
                if result["sources"]:
                    with st.expander("📚 Sources"):
                        for src in result["sources"]:
                            st.markdown(f"**Source {src['id']}** (score: {src['score']:.3f})")
                            st.text(src["text"])
                            st.json(src["metadata"])
                
                # Feedback
                col1, col2 = st.columns([1, 10])
                with col1:
                    if st.button("👍"):
                        st.success("Thanks for feedback!")
                with col2:
                    if st.button("👎"):
                        st.warning("Feedback logged for improvement")
                
                # Save assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"]
                })
                
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("Make sure the API is running: `python -m src.api.main`")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    **TrafficLawBot** helps you understand:
    - Motor Vehicles Act 1988/2019
    - Traffic fines & penalties
    - Telangana/Hyderabad rules
    - E-challan information
    
    **Disclaimer**: For informational purposes only. 
    Consult official sources for legal advice.
    """)
    
    st.header("📊 Example Questions")
    examples = [
        "What is the fine for riding without helmet in Hyderabad?",
        "Drunk driving penalty in Telangana 2026?",
        "How to pay traffic challan online?",
        "What is Section 185 of Motor Vehicles Act?"
    ]
    for ex in examples:
        if st.button(ex, key=ex):
            st.session_state.messages.append({"role": "user", "content": ex})
            st.rerun()
