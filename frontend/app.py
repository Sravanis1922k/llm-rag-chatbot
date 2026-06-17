"""
ARIA — Streamlit Frontend
"""
import streamlit as st
import requests
import time

API = "http://localhost:8000"

st.set_page_config(page_title="ARIA — Academic Assistant", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.main-title { font-size: 2.2rem; font-weight: 700; color: #2B5CE6; }
.sub-title   { color: #666; font-size: 1rem; margin-top: -10px; margin-bottom: 20px; }
.answer-box  { background: #f0f4ff; border-left: 4px solid #2B5CE6;
               padding: 1rem 1.2rem; border-radius: 6px; margin: 12px 0; }
.source-pill { display:inline-block; background:#e8f0fe; color:#2B5CE6;
               border-radius:20px; padding:2px 12px; font-size:12px; margin:3px; }
.metric-box  { background:#fff; border:1px solid #e0e0e0; border-radius:8px;
               padding:12px; text-align:center; }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown('<div class="main-title">🎓 ARIA</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Academic Retrieval & Intelligence Assistant</div>', unsafe_allow_html=True)

# Sidebar — document upload
with st.sidebar:
    st.header("📁 Knowledge Base")
    uploaded = st.file_uploader("Upload documents", type=["txt","pdf","md"], accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            with st.spinner(f"Indexing {f.name}..."):
                res = requests.post(f"{API}/ingest", files={"file": (f.name, f, f.type)})
                if res.status_code == 200:
                    d = res.json()
                    st.success(f"✅ {f.name} — {d['chunks']} chunks indexed")
                else:
                    st.error(f"❌ Failed to index {f.name}")

    st.divider()
    st.header("⚙️ Settings")
    top_k = st.slider("Chunks to retrieve", 1, 10, 5)

    st.divider()
    st.header("📄 Indexed Documents")
    try:
        docs = requests.get(f"{API}/documents").json()
        if docs["count"] == 0:
            st.info("No documents indexed yet.")
        for d in docs["documents"]:
            st.markdown(f"• {d}")
    except:
        st.warning("Backend not reachable")

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            for s in msg["sources"]:
                st.markdown(f'<span class="source-pill">📄 {s}</span>', unsafe_allow_html=True)
        if msg.get("latency"):
            st.caption(f"⚡ {msg['latency']}s · {msg.get('chunks',0)} chunks retrieved")

if prompt := st.chat_input("Ask a question about your documents…"):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                res = requests.post(f"{API}/chat", json={"query": prompt, "top_k": top_k})
                if res.status_code == 200:
                    data = res.json()
                    st.markdown(f'<div class="answer-box">{data["answer"]}</div>', unsafe_allow_html=True)
                    if data["sources"]:
                        for s in data["sources"]:
                            st.markdown(f'<span class="source-pill">📄 {s}</span>', unsafe_allow_html=True)
                    st.caption(f"⚡ {data['latency_seconds']}s · {data['chunks_retrieved']} chunks retrieved")
                    st.session_state.messages.append({
                        "role": "assistant", "content": data["answer"],
                        "sources": data["sources"], "latency": data["latency_seconds"],
                        "chunks": data["chunks_retrieved"]
                    })
                else:
                    st.error("Backend error. Is the server running?")
            except Exception as e:
                st.error(f"Connection error: {e}")
