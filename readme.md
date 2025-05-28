# 🏥 Medical Chatbot

A two-tier RAG (**R**etrieval-**A**ugmented **G**eneration) chatbot for Israeli
HMOs.  
It combines:

* **FastAPI** – REST backend, validates profiles, calls the LLM.
* **Streamlit** – lightweight front-end chat UI.
* **Azure OpenAI** – both for answer generation and profile extraction.
* **Semantic search** over HTML knowledge-base snippets.

---

## ✨ Features

| Phase | What happens |
|-------|--------------|
| **Info-collection** | Chatbot extracts user profile fields (name, age. HMO, tier etc.,) from free-text and asks follow-up questions until complete. |
| **Q & A** | Bot uses the profile + semantic-search snippets to answer questions regarding HMO services. |

---

## ⚙️ Environment variables

Create **`.env`** in the repo root (loaded automatically by `python-dotenv`) and add these fields:

```dotenv
# Document Intelligence
FORM_RECOGNIZER_ENDPOINT=
FORM_RECOGNIZER_KEY=

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_EMBEDDING=
AZURE_OPENAI_API_VERSION=2024-02-15-preview 
```

---

## 🔧 Quick-start

```bash
# 1 · Clone
git clone https://github.com/<your-org>/medical-chatbot.git
cd medical-chatbot

# 2 · Create Python 3.10 venv
python -m venv .venv
source .venv/bin/activate

# 3 · Install deps
pip install -r requirements.txt

# 4 · Supply API keys
cp .env.example .env           # edit OPENAI_API_KEY / AZURE_* keys

# 5 · Launch back-end
python api/main.py                 # http://localhost:8000  (hot-reloading: uvicorn main:app --reload)

# 6 · Launch front-end (new terminal)
streamlit run frontend/ui.py            # http://localhost:8501
