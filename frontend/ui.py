import streamlit as st
import requests
import json

API_URL = "http://localhost:8000/chat"
    
st.set_page_config(page_title="HMO Chatbot", layout="wide")
st.title("🏥 Health Maintenance Organization (HMO) ChatBot")

# ───────────────────────── Session-state init ────────────────────────────
if "phase" not in st.session_state:
    st.session_state.phase = "info_collection"
    st.session_state.history = []  # chat history list[dict]
    st.session_state.profile = {}  # filled UserInfo dict

# col_chat, col_profile = st.columns([3, 1])


# ───────────────────────── Helper: call backend ──────────────────────────
def call_backend(payload: dict):
    """Call the backend API and return the response."""
    try:
        r = requests.post(API_URL, json=payload, timeout=60)
        r.raise_for_status()  # raises on 4xx / 5xx
        if "application/json" in r.headers.get("content-type", ""):
            return r.json()  # fine – ChatResponse
        return json.loads(r.text)  # try best-effort parse
    except (requests.HTTPError, json.JSONDecodeError) as e:
        st.error(f"❌ Backend error {r.status_code}: {r.text[:300]}")
        return None
    except requests.RequestException as e:
        st.error(f"❌ Could not reach backend: {e}")
        return None
    
# ───────────────────────── Render chat history ───────────────────────────
for msg in st.session_state.history:
    st.chat_message(msg["role"]).write(msg["content"])


# ───────────────────────── Handle user input ─────────────────────────────
if prompt := st.chat_input("Your message..."):
    user_lang = st.session_state.get("last_lang", "en")  # default to English

    payload = {
        "phase": st.session_state.phase,
        "message": prompt,
        "history": st.session_state.history
        # "user_info": st.session_state.profile,
    }
    
    # Only include user_info once we actually have it.
    if st.session_state.profile:
        payload["user_info"] = st.session_state.profile

    response = call_backend(payload)
    
    if response:
        st.session_state.history = response["history"]
        st.session_state.profile = response["user_info"]
        
        # Backend declares profile complete
        if response.get("full_info"):                
            st.session_state.phase = "qa"


    st.experimental_rerun()